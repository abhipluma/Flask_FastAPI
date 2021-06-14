from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import engine, get_db
from sqlalchemy.orm import Session
from models import AuthUser, Client, ClientGroup, Coach, Notes, HRPartnerMapping, NumberofPeopleReporting, Country, \
    Language, ClientExtraInfo
from fastapi import APIRouter, Depends, HTTPException, status, Response
import models
from sqlalchemy import distinct, func, desc, or_, and_

models.Base.metadata.create_all(bind=engine)
from datetime import datetime
import pytz
from fastapi.responses import StreamingResponse
import io
import pandas as pd
from export_column import columns_map

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


def convert_to_timezone_with_offset(date_val: datetime, tz: str, converted: bool = False, isoformat: bool = True,
                                    no_offset: bool = True):
    """
    Converting tz-aware datetime object to local tz string with offset
    Args:
        date: tz-aware datetime object
        tz:   local timezone
    Returns: local naive datetime string with offset
    """
    try:
        date_val = datetime.strptime(date_val, '%Y-%m-%dT%H:%M:%S.%f%z')
        if not isinstance(date_val, datetime) and type(date_val) is not str:
            date_val = datetime.combine(date_val, datetime.min.time())

        if converted:
            res = date_val.replace(tzinfo=pytz.timezone(tz))
        else:
            res = date_val.astimezone(pytz.timezone(tz))

        if isoformat:
            if no_offset:
                res = res.replace(tzinfo=None)
            return res.isoformat()
        return res
    except Exception as e:
        print('%s: (%s)' % (type(e), e))


def get_progress_data(client, db):
    logged_in_time = None
    flag_data = client.client_extra_info.first().data
    first_time_password_change = flag_data.get("first_time_password_change")
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

    return {
        "logged_in": first_time_password_change.get("completed"),
        "logged_in_time": logged_in_time.strftime('%m/%d/%Y') if logged_in_time else None,
        "changed_coach": flag_data["coach_changed"]["completed"],
        "invited_360_num": invited_360_num,
        "completed_360_num": completed_360_num,
        "selected_focus_areas": flag_data["focus_area"]['completed'],
        "coach_name": coach_name,
        "reassessment_opened": client.show_reassessment_by_csm,
        "reassessment_complete": flag_data['reassessment_complete']['completed']
    }


my_filter = { "active": and_(Client.inactive_flag == False, Client.paused_flag == False,
                     Client.engagement_complete == False, Client.is_deactivated == False),
            "paused": or_(Client.inactive_flag == True, Client.paused_flag == True),
            "completed": and_(Client.engagement_complete == True),
            "deactivated": and_(Client.is_deactivated == True)}
@app.get("/client-metrics/{status}/{group_id}/")
def client_metrics(request: Request, status: str, group_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_clients = db.query(Client, ClientGroup, AuthUser, Notes, HRPartnerMapping).\
        join(Notes, Notes.client_id == Client.id, isouter=True). \
        join(HRPartnerMapping, HRPartnerMapping.client_id == Client.id, isouter=True). \
        filter(Client.group_id == ClientGroup.id, Client.user_id == AuthUser.id). \
        filter(ClientGroup.take_assessment_only == False, Client.is_test_account == False)
    
    if group_id != 'all':
        db_clients = db_clients.filter(Client.group_id == int(group_id))

    try:
        filters = my_filter[status]
        db_clients = db_clients.filter(filters).filter(
            Client.is_deactivated == False).offset(skip).limit(limit).all()
    except:
        db_clients = db_clients.offset(skip).limit(limit).all()
    
    data = []
    for db_client in db_clients:
        client, group, user, note, hr_partner = db_client
        progress_data = get_progress_data(client, db)
        data.append({
            "id": client.id,
            "client_name": "%s %s" % (client.firstName, client.lastName),
            "client_email": client.email,
            "group": group.display_name,
            "zip_code": client.zipCode,
            "education": client.highestEducation,
            "role": client.your_role,
            "notes": note.notes if note else '',
            "hr_partner": "%s %s" % (hr_partner.hr_first_name, hr_partner.hr_last_name) if hr_partner else '',
            "number_of_people_reporting": client.client_numberofpeoplereporting.option
            if client.client_numberofpeoplereporting else '',
            "country": client.client_country.country if client.client_country else '',
            "language": client.client_language.language if client.client_language else '',
            'manager_call_count': client.client_manager_three_way_call.count()
            if client.client_manager_three_way_call.first() is not None else '',
            "progress": progress_data
        })
    if 'export' in request.query_params and request.query_params['export'] == 'true':
        records = pd.DataFrame(pd.json_normalize(data, sep='_'))
        records = records.filter(columns_map.keys()).rename(columns=columns_map)
        stream = io.StringIO()
        records.to_csv(stream, index = False)
        response = StreamingResponse(iter([stream.getvalue()]),
                            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = "attachment; filename=export.csv"
        return response
    return data

# progress = serializers.SerializerMethodField()
