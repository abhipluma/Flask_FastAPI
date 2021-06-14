from flask import request, jsonify, make_response
from datetime import datetime
import pandas as pd
from sqlalchemy import desc

from export_column import columns_map
from flask_models import AuthUser, Client, ClientGroup, Coach, EngagementExtendInfo, \
    EngagementTracker, Skill

from flask_test import app, db

from utils import convert_to_timezone_with_offset


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
    print(flag_data.get("first_time_password_change"))
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
def client_metrics(status, group_id, skip=0, limit=100):
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


if __name__ == "__main__":
    app.run(debug=True)
