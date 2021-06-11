from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, get_db
from sqlalchemy.orm import Session
from models import AuthUser, Client, ClientGroup, Coach, Notes, HRPartnerMapping, NumberofPeopleReporting, Country, Language
from fastapi import APIRouter, Depends, HTTPException, status
import models
from sqlalchemy import distinct, func, desc, or_
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise App",description="API Doc")#,docs_url=None, redoc_url=None)

app.add_middleware(CORSMiddleware)

@app.get("/user")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_users = db.query(AuthUser)
    users = db_users.offset(skip).limit(limit).all()
    return {'data':users, 'count':db_users.count()}

@app.get("/dashboard-menu/")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # db_users = db.query(Client)
    # users = db_users.offset(skip).limit(limit).all()

    company_id = 3

    all_clients = db.query(Client, ClientGroup, AuthUser).\
    filter(Client.group_id == ClientGroup.id, Client.user_id == AuthUser.id).\
    filter(ClientGroup.take_assessment_only == False, Client.is_test_account == False, Client.company_id==company_id)

    engaged_clients = all_clients.filter(Client.inactive_flag==False, Client.paused_flag==False,
    Client.engagement_complete==False, Client.is_deactivated==False, AuthUser.is_active==True)
    completed_clients = all_clients.filter(Client.engagement_complete==True)
    deactivated_clients = all_clients.filter(Client.is_deactivated==True)
    paused_clients = all_clients.filter(Client.is_deactivated==False)\
        .filter(or_(Client.inactive_flag==True, Client.paused_flag==True))
    
    assessment_only_clients = db.query(Client, ClientGroup, AuthUser).\
    filter(Client.group_id == ClientGroup.id, Client.user_id == AuthUser.id).\
    filter(ClientGroup.take_assessment_only == True, Client.is_test_account == False, Client.company_id==company_id)

    internal_coaches =  db.query(Coach).\
    filter(Coach.is_test_account==False, Coach.inactive_flag==False, Coach.is_external_coach==True, Coach.company_id==company_id)

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



@app.get("/client-metrics/active/{group_id}/")
def client_metrics(group_id:int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_clients = db.query(Client, ClientGroup, AuthUser).\
    filter(Client.group_id == ClientGroup.id, Client.user_id == AuthUser.id).\
    filter(ClientGroup.take_assessment_only == False, Client.is_test_account == False, Client.group_id==group_id).offset(skip).limit(limit).all()
    data = []
    for db_client in db_clients:
        client, group, user = db_client
        data.append({
            "client_name": "%s %s"%(client.firstName, client.lastName),
            "client_email": client.email,
            "group": group.display_name,
            "zip_code": client.zipCode,
            "education": client.highestEducation,
            "role": client.your_role,
            "notes": db.query(Notes).filter( Notes.client_id==client.id).first().notes 
            if db.query(Notes).filter( Notes.client_id==client.id).first() else '',
            "hr_partner": db.query(HRPartnerMapping).filter( HRPartnerMapping.client_id==client.id).first().hr_first_name
            + ' ' + db.query(HRPartnerMapping).filter( HRPartnerMapping.client_id==client.id).first().hr_last_name
            if db.query(HRPartnerMapping).filter( HRPartnerMapping.client_id==client.id).first() else '',
            "number_of_people_reporting": client.client_numberofpeoplereporting.option
            if client.client_numberofpeoplereporting else '',
            "country": client.client_country.country if client.client_country else '',
            "language": client.client_language.language if client.client_language else ''
        })
    return data


# progress = serializers.SerializerMethodField()
# manager_call_count = serializers.SerializerMethodField()
