import pandas
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import engine, get_db
from sqlalchemy.orm import Session
from models import AuthUser, Client, ClientGroup, Coach, EngagementExtendInfo, \
    EngagementTracker, Skill
from fastapi import Depends
import models
from sqlalchemy import desc, or_, and_, text

models.Base.metadata.create_all(bind=engine)
from datetime import datetime
from fastapi.responses import StreamingResponse
import io
import pandas as pd
from export_column import columns_map
from utils import convert_to_timezone_with_offset

app = FastAPI(title="Enterprise App", description="API Doc")  # ,docs_url=None, redoc_url=None)

app.add_middleware(CORSMiddleware)


@app.get("/user")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_users = db.query(AuthUser)
    users = db_users.offset(skip).limit(limit).all()
    return {'data': users, 'count': db_users.count()}


@app.get("/dashboard-menu/")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # db_users = db.query(Client)
    # users = db_users.offset(skip).limit(limit).all()

    company_id = 3

    all_clients = db.query(Client, ClientGroup, AuthUser). \
        filter(Client.group_id == ClientGroup.id, Client.user_id == AuthUser.id). \
        filter(ClientGroup.take_assessment_only == False, Client.is_test_account == False,
               Client.company_id == company_id)

    engaged_clients = all_clients.filter(Client.inactive_flag == False, Client.paused_flag == False,
                                         Client.engagement_complete == False, Client.is_deactivated == False,
                                         AuthUser.is_active == True)
    completed_clients = all_clients.filter(Client.engagement_complete == True)
    deactivated_clients = all_clients.filter(Client.is_deactivated == True)
    paused_clients = all_clients.filter(Client.is_deactivated == False) \
        .filter(or_(Client.inactive_flag == True, Client.paused_flag == True))

    assessment_only_clients = db.query(Client, ClientGroup, AuthUser). \
        filter(Client.group_id == ClientGroup.id, Client.user_id == AuthUser.id). \
        filter(ClientGroup.take_assessment_only == True, Client.is_test_account == False,
               Client.company_id == company_id)

    internal_coaches = db.query(Coach). \
        filter(Coach.is_test_account == False, Coach.inactive_flag == False, Coach.is_external_coach == True,
               Coach.company_id == company_id)

    data = {
        "has_engaged_clients": engaged_clients.first() is not None,
        "has_completed_clients": completed_clients.first() is not None,
        "has_deactivated_clients": deactivated_clients.first() is not None,
        "has_paused_clients": paused_clients.first() is not None,
        "has_take_assessment_only_clients": assessment_only_clients.first() is not None,
        "has_internal_coaches": internal_coaches.first() is not None,
    }

    has_assessment_only = data['has_take_assessment_only_clients']

    # engagement stats
    engagement_stats = {'menu_title': 'Engagement Stats', 'menu_items': []}
    # engagement stats - 1:1
    tabs = list()
    if data['has_completed_clients']:
        tabs.append({'title': 'Completed engagements', 'code': 'completed_engagement'})
    if data['has_deactivated_clients']:
        tabs.append({'title': 'Deactivated engagements', 'code': 'deactivated_engagement'})
    if data['has_engaged_clients']:
        tabs.append({'title': 'Engagement metrics', 'code': 'engagement_metrics'})
    if data['has_paused_clients']:
        tabs.append({'title': 'Paused engagements', 'code': 'paused_engagement'})
    engagement_stats['menu_items'].append(
        {
            'title': '1:1 Coaching',
            'tabs': tabs
        }
    )
    if has_assessment_only:
        # engagement stats - Assessment Only
        engagement_stats['menu_items'].append(
            {
                'title': 'Assessment Only',
                'tabs': [{
                    'title': 'Engagement metrics',
                    'code': 'engagement_metrics'
                }]
            }
        )

    # Assessment Stats
    assessment_stats = {'menu_title': 'Assessment Stats', 'menu_items': []}
    # assessment stats - 1:1
    assessment_stats['menu_items'].append({
        'title': '1:1 Coaching',
        'tabs': [
            {'title': 'Results by Skill', 'code': 'result_by_skills'},
            {'title': 'Results by Skill Category', 'code': 'results_by_skill_category'},
            {'title': 'Reassessment Results', 'code': 'reassessment_results'},
        ]
    })

    if has_assessment_only:
        # assessment stats - Assessment Only
        assessment_stats['menu_items'].append({
            'title': 'Assessment Only',
            'tabs': [
                {'title': 'Results by Skill', 'code': 'result_by_skills'},
                {'title': 'Results by Skill Category', 'code': 'results_by_skill_category'}
            ]
        })

    # Survey Stats
    survey_stats = {'menu_title': 'Survey Stats', 'menu_items': []}
    # survey stats - 1:1
    survey_stats['menu_items'].append({
        'title': '1:1 Coaching',
        'tabs': [
            {'title': 'Initial Leadership Sentiment Survey Results',
             'code': 'initial_leadership_sentiment_survey_results'},
            {'title': 'Reassessment Leadership Sentiment Survey Results',
             'code': 'reassessment_leadership_sentiment_survey_results'}
        ]
    })
    response_data = {'menus': [engagement_stats, assessment_stats, survey_stats]}
    # internal coaches
    if data['has_internal_coaches']:
        internal_coaches = {'menu_title': 'Coaches', 'menu_items': []}
        response_data = {'menus': [engagement_stats, assessment_stats, survey_stats, internal_coaches]}
    return response_data


def get_client_engagement_end_date(client, db):
    engagement_end_date = None
    client_engagement_tracker = client.client_engagement_tracker.filter(EngagementTracker.coach_id == \
                                                                        client.assignedCoach_id).all()
    if client_engagement_tracker:
        engagement_end_date = client_engagement_tracker[0].end_date
    elif client.coach_payment_start_date:
        engagement_end_date = client.coach_payment_start_date + datetime.timedelta(
            days=client.client_contract_info[0].duration)
    return engagement_end_date


def get_progress_data(client, db):
    logged_in_time = None
    flag_data = client.client_extra_info.first().data
    first_time_password_change = flag_data.get("first_time_password_change")
    number_of_focus_areas = 0
    competency_1, competency_2, competency_3, competency_4 = None, None, None, None
    if client.focus_area_client:
        focus_area_client = client.focus_area_client
        number_of_focus_areas = len(focus_area_client)
        focus_area_skill_ids = tuple([i.focus_area_skill.id for i in focus_area_client])
        focus_area_skills = db.query(Skill).filter(Skill.id.in_(focus_area_skill_ids)).all()
        try:
            competency_1 = focus_area_skills[0].skillName
            competency_2 = focus_area_skills[1].skillName
            competency_3 = focus_area_skills[2].skillName
            competency_4 = focus_area_skills[3].skillName
        except:
            pass

    if first_time_password_change.get("completed") and \
            first_time_password_change.get("completed_on"):
        logged_in_time = convert_to_timezone_with_offset(first_time_password_change.get("completed_on"),
                                                         'America/Los_Angeles', isoformat=False)

    coach = db.query(Coach).filter(
        Coach.id == client.assignedCoach_id).first() if client.assignedCoach_id else ''
    coach_name = '%s %s' % (coach.firstName, coach.lastName) if coach else ''
    test = {"Manager": 0,
            "Peer team member": 0,
            "Direct report": 0,
            "Cross-functional colleague": 0}

    invited_360_num = None
    completed_360_num = 0
    if client.client_user.answer_mapper_user:
        for i in client.client_user.answer_mapper_user:
            if i.is_reassessment == False and i.answered_by_id:
                test[i.answer_mapper_answered_by.related_as] += 1
                completed_360_num += 1 if i.answered else 0
        invited_360_num = ", ".join(["%s - %s" % (k.replace('_', " "), v) for k, v in test.items() if v])

    engagement_end_date = get_client_engagement_end_date(client, db)
    if engagement_end_date:
        engagement_end_date = convert_to_timezone_with_offset(engagement_end_date, 'America/Los_Angeles',
                                                              isoformat=False)
    try:
        extend_info = client.client_engagement_extend.filter(
            EngagementExtendInfo.coach_id == client.assignedCoach_id).order_by(
            desc(EngagementExtendInfo.extended_on)).all()
        engagement_extended_date = convert_to_timezone_with_offset(extend_info[0].extended_on, 'America/Los_Angeles',
                                                                   isoformat=False).strftime('%m/%d/%Y')
    except:
        engagement_extended_date = None
    return {
        "logged_in": first_time_password_change.get("completed"),
        "logged_in_time": logged_in_time.strftime('%m/%d/%Y') if logged_in_time else None,
        "changed_coach": flag_data["coach_changed"]["completed"],
        "invited_360_num": invited_360_num,
        "completed_360_num": completed_360_num,
        "selected_focus_areas": flag_data["focus_area"]['completed'],
        "coach_name": coach_name,
        "reassessment_opened": client.show_reassessment_by_csm,
        "reassessment_complete": flag_data['reassessment_complete']['completed'] if \
            flag_data.get('reassessment_complete') else None,
        "number_of_focus_areas": number_of_focus_areas,
        "competency_1": competency_1,
        "competency_2": competency_2,
        "competency_3": competency_3,
        "competency_4": competency_4,
        "engagement_end_date": engagement_end_date.strftime('%m/%d/%Y') if engagement_end_date else None,
        "engagement_extended_date": engagement_extended_date
    }


my_filter = {"active": and_(Client.inactive_flag == False, Client.paused_flag == False,
                            Client.engagement_complete == False, Client.is_deactivated == False),
             "paused": or_(Client.inactive_flag == True, Client.paused_flag == True),
             "completed": and_(Client.engagement_complete == True),
             "deactivated": and_(Client.is_deactivated == True)}

ordering_keys = {
    'firstName': Client.firstName,
    'email': Client.email,
    '-firstName': desc(Client.firstName),
    '-email': desc(Client.email),
    'group__name': ClientGroup.display_name,
    '-group__name': desc(ClientGroup.display_name),
}


@app.get("/client-metrics/{status}/{group_id}/")
def client_metrics(request: Request, status: str, group_id: str, skip: int = 0, limit: int = 100,
                   db: Session = Depends(get_db)):
    db_clients = db.query(Client, ClientGroup, AuthUser). \
        filter(Client.group_id == ClientGroup.id, Client.user_id == AuthUser.id). \
        filter(ClientGroup.take_assessment_only == False, Client.is_test_account == False)
    if group_id != 'all':
        db_clients = db_clients.filter(Client.group_id == int(group_id))

    try:
        filters = my_filter[status]
        db_clients = db_clients.filter(filters)
    except:
        pass

    if 'ordering' in request.query_params:
        db_clients = db_clients.order_by(ordering_keys.get(request.query_params['ordering']))
    else:
        db_clients = db_clients.order_by(desc(Client.id))

    if 'export' not in request.query_params:
        db_clients = db_clients.offset(skip).limit(limit).all()
    else:
        db_clients = db_clients.all()

    data = []
    for db_client in db_clients:
        client, group, user = db_client
        progress_data = get_progress_data(client, db)
        data.append({
            "id": client.id,
            "client_name": "%s %s" % (client.firstName, client.lastName),
            "client_email": client.email,
            "group": group.display_name,
            "zip_code": client.zipCode,
            "education": client.highestEducation,
            "role": client.your_role,
            "notes": client.client_notes.first().notes if client.client_notes.first() else '',
            "hr_partner": "%s %s" % (client.hr_partner.first().hr_first_name, client.hr_partner.first().hr_last_name)
            if client.hr_partner.first() else '',
            "number_of_people_reporting": client.client_numberofpeoplereporting.option
            if client.client_numberofpeoplereporting else '',
            "country": client.client_country.country if client.client_country else '',
            "language": client.client_language.language if client.client_language else '',
            'manager_call_count': client.client_manager_three_way_call.count()
            if client.client_manager_three_way_call.first() is not None else 0,
            "progress": progress_data
        })
    if 'export' in request.query_params and request.query_params['export'] == 'true':
        records = pd.DataFrame(pd.json_normalize(data, sep='_'))
        records = records.filter(columns_map.keys()).rename(columns=columns_map)
        stream = io.StringIO()
        records.to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]),
                                     media_type="text/csv"
                                     )
        response.headers["Content-Disposition"] = "attachment; filename=export.csv"
        return response
    return data


@app.get("/client/")
def client(request: Request, db: Session = Depends(get_db), skip=0, limit=100):
    data = []
    if 'sql' in request.query_params:
        sql = text('''
                   select "id", CONCAT("firstName", "lastName") as "client_name", "email" as "client_email",
                   "your_role" as "role", "zipCode" as "zip_code", "highestEducation" as "education", 
                   (select "display_name" AS "group" FROM client_onboarding_clientgroup as CG where CG.id=COC.group_id ), 
                   (select "language" FROM coach_onboarding_language as CL where CL.id=COC.preferred_language_id ),
                   (select "country" FROM coach_onboarding_country as CC where CC.id=COC.country_id ),
                   (select "option" AS "number_of_people_reporting" FROM client_onboarding_numberofpeoplereporting as CPR where CPR.id=COC.number_of_people_reporting_id),
                   (select CONCAT(EDHP.hr_first_name, EDHP.hr_last_name) as hr_partner from enterprice_dashboard_hrpartnermapping as EDHP where EDHP.client_id=COC.id limit 1),
                   (select count(*) as manager_call_count from chat_managerthreewaycallsession as CMTCS where CMTCS.client_id=COC.id),
                   (select notes from enterprice_dashboard_notes as EDN where EDN.client_id=COC.id limit 1),
                   (select CONCAT("firstName", "lastName") AS "coach_name" FROM coach_onboarding_coach as coach where coach.id="assignedCoach_id")
                   from client_onboarding_client as COC WHERE COC.is_test_account = false  
                   ''')
        sql_df = pandas.read_sql(
            sql,
            con=engine
        )
        data = sql_df.to_dict('records')
    else:
        db_clients = db.query(Client).all()
        data = db_clients
        # for db_client in db_clients:
        #     data.append({"firstName": db_client.firstName})
    return data