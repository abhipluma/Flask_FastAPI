import pandas
from flask import request, jsonify, make_response
from datetime import datetime
import pandas as pd
from sqlalchemy import desc
import pytz

from export_column import columns_map
from flask_models import AuthUser, Client, ClientGroup, Coach, EngagementExtendInfo, \
    EngagementTracker, Skill

from flask_test import app, db

from utils import convert_to_timezone_with_offset
from sqlalchemy import text


def get_client_engagement_end_date(client):
    engagement_end_date = None
    client_engagement_tracker = client.client_engagement_tracker.filter(
        EngagementTracker.coach_id == client.assignedCoach_id).all()
    if client_engagement_tracker:
        engagement_end_date = client_engagement_tracker[0].end_date
    elif client.coach_payment_start_date:
        engagement_end_date = client.coach_payment_start_date + datetime.timedelta(
            days=client.client_contract_info[0].duration)
    return engagement_end_date


def get_progress_data(client):
    logged_in_time = None
    flag_data = client.client_extra_info.first().data
    first_time_password_change = flag_data.get("first_time_password_change")
    number_of_focus_areas = 0
    competency_1, competency_2, competency_3, competency_4 = None, None, None, None
    if client.focus_area_client:
        focus_area_client = client.focus_area_client
        number_of_focus_areas = len(focus_area_client)
        focus_area_skill_ids = tuple([i.focus_area_skill.id for i in focus_area_client])
        focus_area_skills = db.session.query(Skill).filter(Skill.id.in_(focus_area_skill_ids)).all()
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
    coach = db.session.query(Coach).filter(
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

    engagement_end_date = get_client_engagement_end_date(client)
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


@app.route("/user")
def get_user():
    users = AuthUser.query.limit(10).all()
    user_list = []
    for user in users:
        user_list.append(user.json())
    return make_response(jsonify({'users': user_list}))


my_filter = {"active": db.and_(Client.inactive_flag == False, Client.paused_flag == False,
                               Client.engagement_complete == False, Client.is_deactivated == False),
             "paused": db.or_(Client.inactive_flag == True, Client.paused_flag == True),
             "completed": db.and_(Client.engagement_complete == True),
             "deactivated": db.and_(Client.is_deactivated == True)}

ordering_keys = {
    'firstName': Client.firstName,
    'email': Client.email,
    '-firstName': desc(Client.firstName),
    '-email': desc(Client.email),
    'group__name': ClientGroup.display_name,
    '-group__name': desc(ClientGroup.display_name),
}


@app.get("/client-metrics/<status>/<group_id>/")
def client_metrics(status, group_id, skip=0, limit=1000):
    db_clients = db.session.query(Client, ClientGroup, AuthUser). \
        filter(Client.group_id == ClientGroup.id, Client.user_id == AuthUser.id). \
        filter(ClientGroup.take_assessment_only == False, Client.is_test_account == False)

    if group_id != 'all':
        db_clients = db_clients.filter(Client.group_id == int(group_id))

    try:
        filters = my_filter[status]
        db_clients = db_clients.filter(filters)
    except:
        pass

    if 'ordering' in request.args:
        db_clients = db_clients.order_by(ordering_keys.get(request.args.get('ordering')))
    else:
        db_clients = db_clients.order_by(desc(Client.id))

    if 'export' not in request.args and request.args.get('export') != 'true':
        db_clients = db_clients.offset(skip).limit(limit).all()
    else:
        db_clients = db_clients.all()

    data = []
    for db_client in db_clients:
        client, group, user = db_client
        progress_data = get_progress_data(client)
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
    if 'export' in request.args and request.args.get('export') == 'true':
        records = pd.DataFrame(pd.json_normalize(data, sep='_'))
        records = records.filter(columns_map.keys()).rename(columns=columns_map)
        resp = make_response(records.to_csv(index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp
    return make_response(jsonify(data))


status_filter = {"active": ''' and COC.inactive_flag = false and COC.paused_flag = false and
                            COC.engagement_complete = false  and COC.is_deactivated = false''',
                 "paused": ''' and (COC.inactive_flag = true or  COC.paused_flag = true)''',
                 "completed": ''' and COC.engagement_complete = true''',
                 "deactivated": ''' and COC.is_deactivated = true '''}

sql_ordering_keys = {
    'firstName': ''' order by "firstName" ''',
    'email': ''' order by "client_email" ''',
    '-firstName': ''' order by "firstName" desc''',
    '-email': ''' order by "client_email" desc''',
    'group__name': ''' order by "group" ''',
    '-group__name': ''' order by "group" ''',
}


@app.get("/client/<status>/<group_id>/")
def client(status, group_id, skip=0, limit=100):
    data = []
    if 'sql' in request.args:
        condition = f'''and COC.group_id={group_id}''' if group_id != 'all' and group_id.isnumeric() else ''''''
        condition += f'''{status_filter.get(status)}''' if status != 'all' and status in status_filter else ''''''
        condition += sql_ordering_keys.get(
            request.args.get('ordering')) if 'ordering' in request.args and \
            request.args.get('ordering') in sql_ordering_keys else ''' order by COC.id desc'''

        sql = text('''
               select COC."id", CONCAT("firstName", "lastName") as "client_name", COC."email" as "client_email",
               "your_role" as "role", "zipCode" as "zip_code", "highestEducation" as "education", 
               (select "display_name" AS "group" FROM client_onboarding_clientgroup as CG where CG.id=COC.group_id ), 
               (select "language" FROM coach_onboarding_language as CL where CL.id=COC.preferred_language_id ),
               (select "country" FROM coach_onboarding_country as CC where CC.id=COC.country_id ),
               (select "option" AS "number_of_people_reporting" FROM client_onboarding_numberofpeoplereporting as CPR where CPR.id=COC.number_of_people_reporting_id),
               (select CONCAT(EDHP.hr_first_name, EDHP.hr_last_name) as hr_partner from enterprice_dashboard_hrpartnermapping as EDHP where EDHP.client_id=COC.id limit 1),
               (select count(*) as manager_call_count from chat_managerthreewaycallsession as CMTCS where CMTCS.client_id=COC.id),
               (select count(*) as number_of_focus_areas from client_onboarding_focusareaskillselection as COFASS where COFASS.client_id=COC.id),
               (select notes from enterprice_dashboard_notes as EDN where EDN.client_id=COC.id limit 1),
               (select CONCAT("firstName", "lastName") AS "coach_name" FROM coach_onboarding_coach as coach where coach.id="assignedCoach_id"),
               (select "option" AS "number_of_people_reporting" FROM client_onboarding_numberofpeoplereporting as CPR where CPR.id=COC.number_of_people_reporting_id ),
               (select "data"->'first_time_password_change'->'completed' as logged_in
                FROM client_onboarding_clientextrainfo as CEI where CEI.client_id=COC.id),
                (select "data"->'first_time_password_change'->'completed_on' as logged_in_time
                FROM client_onboarding_clientextrainfo as CEI where CEI.client_id=COC.id),
                (select "data"->'coach_changed'->'completed' as coach_changed
                FROM client_onboarding_clientextrainfo as CEI where CEI.client_id=COC.id),
                (select "data"->'focus_area'->'completed' as focus_area
                FROM client_onboarding_clientextrainfo as CEI where CEI.client_id=COC.id),
                (select "data"->'reassessment_complete'->'completed' as reassessment_complete
                FROM client_onboarding_clientextrainfo as CEI where CEI.client_id=COC.id),
                (select COALESCE("end_date"::date::text, COC.coach_payment_start_date::date::text) AS "engagement_end_date" 
                FROM client_onboarding_engagementtracker as COET where COET.client_id = COC.id AND COET.coach_id = "assignedCoach_id" and COET.end_date is not null limit 1),
                (select COALESCE("extended_on"::date::text, null) AS "engagement_extend_date" 
                FROM client_onboarding_engagementextendinfo as COEEI where COEEI.client_id = COC.id AND COEEI.coach_id = "assignedCoach_id" and COEEI.extended_on is not null limit 1),
                (select count(*) AS "completed_360_num" FROM exercise_useranswermapper as EUAM 
                where EUAM.user_id=COC.user_id and EUAM.is_reassessment = False and EUAM.answered_by_id is not null and EUAM.answered =True ),
                (select invited_360_num as invited_360_num from (select user_id, concat(
                case when sum(Manager_count) = 0 then '' else concat('Manager -', sum(Manager_count)) end,
                case when sum(direct_report) = 0 then '' else concat(', Direct report -', sum(direct_report)) end,
                case when sum(cross_function_colleague) = 0 then '' else concat(', Cross-functional colleague -', sum(cross_function_colleague)) end,
                case when sum(peer_team_member) = 0 then '' else concat(', Peer team member -', sum(peer_team_member)) end
                ) as invited_360_num from (select EUAM.user_id,
                (count(case when EPAE.related_as = 'Manager' then 1 else Null end)) as Manager_count,
                (count(case when EPAE.related_as = 'Direct report' then 1 else Null end)) as direct_report,
                (count(case when EPAE.related_as = 'Cross-functional colleague' then 1 else Null end)) as cross_function_colleague,
                (count(case when EPAE.related_as = 'Peer team member' then 1 else Null end)) as peer_team_member
                FROM exercise_useranswermapper as EUAM 
                inner join exercise_peopleansweringexercise as EPAE on EPAE.id=EUAM.answered_by_id
                where EUAM.is_reassessment = False and EUAM.answered_by_id is not null and EUAM.answered =True
                group by EPAE.related_as, EUAM.user_id) RRC group by user_id) as UAM where UAM.user_id = COC.user_id),
                (select competency from (select client_id,string_agg(CDS."skillName", ', ') as competency from client_onboarding_focusareaskillselection as COFASS
                inner join coach_dashboard_skill CDS on CDS.id =  COFASS.focus_area_skill_id group by client_id) COMP where COMP.client_id= COC.id)
               from client_onboarding_client as COC 
               inner join client_onboarding_clientgroup COCG on COCG.id = COC.group_id
               inner join auth_user AU on AU.id = COC.user_id
               WHERE COC.is_test_account = false and COCG.take_assessment_only = false
                ''' + condition)

        sql_df = pandas.read_sql(
            sql,
            con=db.engine,
        )
        data = sql_df.to_dict('records')
    else:
        db_clients = db.session.query(Client).all()
        for db_client in db_clients:
            data.append({"firstName": db_client.firstName})

    if 'export' in request.args and request.args.get('export') == 'true':
        records = pd.DataFrame(pd.json_normalize(data, sep='_'))
        records = records.filter(columns_map.keys()).rename(columns=columns_map)
        resp = make_response(records.to_csv(index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp
    return make_response(jsonify(data))


if __name__ == "__main__":
    app.run(debug=True)
