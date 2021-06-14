from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, JSON
from sqlalchemy.orm import relationship
import datetime

try:
    from .database import Base
except Exception as e:
    from database import Base


class AuthUser(Base):
    __tablename__ = 'auth_user'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    date_joined = Column(DateTime)
    last_login = Column(DateTime)

    client_user = relationship("Client", lazy='dynamic', foreign_keys='Client.user_id', back_populates="client_user")
    answer_mapper_user = relationship("UserAnswerMapper", foreign_keys='UserAnswerMapper.user_id',
                                      back_populates="answer_mapper_user")


class Client(Base):
    __tablename__ = 'client_onboarding_client'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('auth_user.id'))
    inactive_flag = Column(Boolean, default=False, )
    paused_flag = Column(Boolean, default=False, )
    engagement_complete = Column(Boolean, default=False, )
    minimum_number_of_invites_to_see_self_results = Column(Integer, default=5)
    minimum_number_of_people_answered_to_see_others_average = Column(Integer, default=3)
    survey_slug = Column(String, nullable=True)
    contract_duration = Column(Integer, default=180)
    # modules_id = Column(Integer)
    # coach_modules_id = Column(Integer)
    # functional_areas_id = Column(Integer)
    # areas_of_expertise_id = Column(Integer)
    # languages_id = Column(Integer)
    preferred_language_id = Column(Integer, ForeignKey('coach_onboarding_language.id'))
    assignedCoach_id = Column(Integer, nullable=True)
    assigned_csm_id = Column(Integer, nullable=True)
    firstName = Column(String, )
    lastName = Column(String, )
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country_id = Column(Integer, ForeignKey('coach_onboarding_country.id'))
    zipCode = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    age = Column(String, nullable=True)
    highestEducation = Column(String, nullable=True)
    job_level = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    email = Column(String, )
    notes = Column(String, nullable=True)
    notes_by_client = Column(String, nullable=True)
    invalid_password_attempts = Column(Integer, default=0)
    linkedin_info_pdf = Column(String, nullable=True)
    linkedin_public_profile_url = Column(String, nullable=True)
    title_id = Column(Integer, nullable=True, )
    number_of_people_reporting_id = Column(Integer, ForeignKey('client_onboarding_numberofpeoplereporting.id'))
    number_of_people_interacting_id = Column(Integer, nullable=True)
    push_notification_device_token = Column(String, nullable=True)
    allow_push_notification_and_disable_email = Column(Boolean, default=False)
    professional_development_question = Column(String, nullable=True, )
    your_role = Column(String, nullable=True, )
    did_you_have_a_coach = Column(String, nullable=True, )
    coaching_pairing_preference = \
        Column(String, nullable=True, )
    anything_else = Column(String, nullable=True, )
    email_to_sign_in_1 = Column(Boolean, default=False)
    email_to_sign_in_2 = Column(Boolean, default=False)
    career_and_vision_questions_answered = Column(Boolean, default=False)
    exercise_id = Column(Integer, nullable=True, )
    is_hr_person = Column(Boolean, default=False)
    additional_comments = Column(String, nullable=True)
    coach_payment_start_date = Column(DateTime, nullable=True)
    reason_for_coach_pairing = Column(String, nullable=True)
    client_drop_date = Column(DateTime, nullable=True)
    show_conference_call_feedback = Column(Boolean, default=False)
    timezone = Column(String, nullable=True, default="America/Los_Angeles")
    plan = Column(String, nullable=True)
    company_id = Column(Integer, nullable=True, )
    has_materials = Column(Boolean, default=False, )
    client_manager_exercise_slug = Column(String, nullable=True, )
    show_reassessment_by_csm = Column(Boolean, default=False, )
    reassessment_triggered_on = Column(DateTime, nullable=True)
    show_manager_result = Column(Boolean, default=False, )
    show_invitee_comments = Column(Boolean, default=False, )
    show_invitee_additional_feedback = Column(Boolean, default=False, )
    use_new_assessment_view = Column(Boolean, default=False, )
    is_test_account = Column(Boolean, default=False, )
    send_manager_feedback = Column(Boolean, default=False, )
    manager_feedback_frequency = Column(Integer, default=6, )
    should_view_assessment_results = Column(Boolean, default=False, )
    group_id = Column(Integer, ForeignKey('client_onboarding_clientgroup.id'))
    impact_report_file = Column(String, nullable=True)
    import_report_s3_link = Column(String, nullable=True)
    video_test_fail_email_sent_on = Column(DateTime, nullable=True)
    uses_saml_login = Column(Boolean, default=False, )
    uses_new_dashboard = Column(Boolean, default=False, )
    saml_login_idp_id = Column(String, nullable=True, )
    company_sale_id = Column(Integer, nullable=True)
    video_chat_url = Column(String, nullable=True, )
    is_deactivated = Column(Boolean, default=False, )
    should_open_reassessment_section = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=False, )
    assessment_only_plus_two = Column(Boolean, default=False, )

    client_group = relationship("ClientGroup", foreign_keys=[group_id], back_populates="client_group")
    client_user = relationship("AuthUser", foreign_keys=[user_id], back_populates="client_user")
    client_numberofpeoplereporting = relationship("NumberofPeopleReporting",
                                                  foreign_keys=[number_of_people_reporting_id],
                                                  back_populates="client_numberofpeoplereporting")

    client_country = relationship("Country",
                                  foreign_keys=[country_id], back_populates="client_country")

    client_language = relationship("Language",
                                   foreign_keys=[preferred_language_id], back_populates="client_language")

    client_manager_three_way_call = relationship("ManagerThreeWayCallSession", lazy='dynamic',
                                                 foreign_keys='ManagerThreeWayCallSession.client_id',
                                                 back_populates="client_manager_three_way_call")

    client_extra_info = relationship("ClientExtraInfo", lazy='dynamic',
                                     foreign_keys='ClientExtraInfo.client_id', back_populates="client_extra_info")
    focus_area_client = relationship("FocusAreaSkillSelection", foreign_keys='FocusAreaSkillSelection.client_id',
                                     back_populates="focus_area_client")

    client_engagement_tracker = relationship("EngagementTracker", foreign_keys='EngagementTracker.client_id', lazy='dynamic',
                                             back_populates="client_engagement_tracker")
    client_contract_info = relationship("ClientContractInfo", foreign_keys='ClientContractInfo.client_id', lazy='dynamic',
                                        back_populates="client_contract_info")
    client_engagement_extend = relationship("EngagementExtendInfo",
                                            foreign_keys='EngagementExtendInfo.client_id', lazy='dynamic',
                                            back_populates="client_engagement_extend")

    client_notes = relationship("Notes", foreign_keys='Notes.client_id', lazy='dynamic',
                                     back_populates="client_notes")

    hr_partner = relationship("HRPartnerMapping", foreign_keys='HRPartnerMapping.client_id', lazy='dynamic',
                                     back_populates="hr_partner")

class ClientGroup(Base):
    __tablename__ = 'client_onboarding_clientgroup'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    display_name = Column(String, nullable=True)
    take_assessment_only = Column(Boolean, default=False)

    client_group = relationship("Client", lazy='dynamic', foreign_keys='Client.group_id', back_populates="client_group")


class Coach(Base):
    __tablename__ = 'coach_onboarding_coach'
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String)
    lastName = Column(String)
    company_id = Column(Integer)
    is_test_account = Column(Boolean)
    inactive_flag = Column(Boolean)
    is_external_coach = Column(Boolean)
    engagement_tracker_coach = relationship('EngagementTracker', foreign_keys='EngagementTracker.coach_id',
                                            back_populates="engagement_tracker_coach")
    engagement_extend_coach = relationship('EngagementExtendInfo', foreign_keys='EngagementExtendInfo.coach_id',
                                           back_populates="engagement_extend_coach")


class Notes(Base):
    __tablename__ = 'enterprice_dashboard_notes'
    id = Column(Integer, primary_key=True, index=True)
    notes = Column(String)
    client_id = Column(Integer, ForeignKey('client_onboarding_client.id'))
    client_notes = relationship("Client",
                                        foreign_keys=[client_id], back_populates="client_notes")


class HRPartnerMapping(Base):
    __tablename__ = 'enterprice_dashboard_hrpartnermapping'
    id = Column(Integer, primary_key=True, index=True)
    hr_first_name = Column(String)
    hr_last_name = Column(String)

    client_id = Column(Integer, ForeignKey('client_onboarding_client.id'))
    hr_partner = relationship("Client",
                                        foreign_keys=[client_id], back_populates="hr_partner")


class NumberofPeopleReporting(Base):
    __tablename__ = 'client_onboarding_numberofpeoplereporting'
    id = Column(Integer, primary_key=True, index=True)
    option = Column(String)

    client_numberofpeoplereporting = relationship("Client", lazy='dynamic',
                                                  foreign_keys='Client.number_of_people_reporting_id',
                                                  back_populates="client_numberofpeoplereporting")


class Country(Base):
    __tablename__ = 'coach_onboarding_country'
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String)

    client_country = relationship("Client", lazy='dynamic',
                                  foreign_keys='Client.country_id', back_populates="client_country")


class Language(Base):
    __tablename__ = 'coach_onboarding_language'
    id = Column(Integer, primary_key=True, index=True)
    language = Column(String)

    client_language = relationship("Client", lazy='dynamic',
                                   foreign_keys='Client.preferred_language_id', back_populates="client_language")


class ManagerThreeWayCallSession(Base):
    __tablename__ = 'chat_managerthreewaycallsession'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('client_onboarding_client.id'))

    client_manager_three_way_call = relationship("Client",
                                                 foreign_keys=[client_id],
                                                 back_populates="client_manager_three_way_call")


class ClientExtraInfo(Base):
    __tablename__ = 'client_onboarding_clientextrainfo'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('client_onboarding_client.id'))
    data = Column(JSON)

    client_extra_info = relationship("Client",
                                     foreign_keys=[client_id], back_populates="client_extra_info")


class UserAnswerMapper(Base):
    __tablename__ = 'exercise_useranswermapper'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('auth_user.id'))
    answered_by_id = Column(Integer, ForeignKey('exercise_peopleansweringexercise.id'))
    is_reassessment = Column(Boolean)
    answered = Column(Boolean)

    answer_mapper_user = relationship("AuthUser", foreign_keys=[user_id],
                                      back_populates="answer_mapper_user")
    answer_mapper_answered_by = relationship("PeopleAnsweringExercise",
                                             foreign_keys=[answered_by_id], back_populates="answer_mapper_answered_by")


class PeopleAnsweringExercise(Base):
    __tablename__ = 'exercise_peopleansweringexercise'
    id = Column(Integer, primary_key=True, index=True)
    related_as = Column(String)
    answer_mapper_answered_by = relationship("UserAnswerMapper",
                                             foreign_keys='UserAnswerMapper.answered_by_id',
                                             back_populates="answer_mapper_answered_by")


class FocusAreaSkillSelection(Base):
    __tablename__ = 'client_onboarding_focusareaskillselection'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('client_onboarding_client.id'))
    focus_area_skill_id = Column(Integer, ForeignKey('coach_dashboard_skill.id'))

    focus_area_client = relationship("Client", foreign_keys=[client_id],
                                        back_populates="focus_area_client")
    focus_area_skill = relationship("Skill",
                                       foreign_keys=[focus_area_skill_id],
                                       back_populates="focus_area_skill")


class Skill(Base):
    __tablename__ = 'coach_dashboard_skill'
    id = Column(Integer, primary_key=True, index=True)
    skillName = Column(String)
    description = Column(String)

    focus_area_skill = relationship("FocusAreaSkillSelection",
                                       foreign_keys='FocusAreaSkillSelection.focus_area_skill_id',
                                       back_populates="focus_area_skill")


class EngagementTracker(Base):
    __tablename__ = 'client_onboarding_engagementtracker'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('client_onboarding_client.id'))
    coach_id = Column(Integer, ForeignKey('coach_onboarding_coach.id'))
    duration = Column(Integer, default=180)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_sessions = Column(Integer, default=12)
    total_three_way_sessions = Column(Integer, default=0)

    client_engagement_tracker = relationship("Client", foreign_keys=[client_id],
                                                back_populates="client_engagement_tracker")
    engagement_tracker_coach = relationship("Coach", foreign_keys=[coach_id],
                                               back_populates="engagement_tracker_coach")


class ClientContractInfo(Base):
    __tablename__ = 'client_onboarding_clientcontractinfo'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('client_onboarding_client.id'))
    duration = Column(Integer, default=0)
    duration_in_months = Column(Float, default=0)
    session_num = Column(Integer, default=0)
    three_way_session_num = Column(Integer, default=0)
    session_frequency = Column(Integer, default=0)
    session_length = Column(Integer, default=0)

    client_contract_info = relationship("Client", foreign_keys=[client_id],
                                           back_populates="client_contract_info")


class EngagementExtendInfo(Base):
    __tablename__ = 'client_onboarding_engagementextendinfo'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('client_onboarding_client.id'))
    coach_id = Column(Integer, ForeignKey('coach_onboarding_coach.id'))
    extended_on = Column(DateTime)
    extended_duration = Column(Integer, default=0)
    should_extend_sessions = Column(Boolean, default=True)
    extended_sessions = Column(Integer, default=0)
    extended_three_way_sessions = Column(Integer, default=0)
    is_paid = Column(Boolean, default=True)

    client_engagement_extend = relationship("Client", foreign_keys=[client_id],
                                                back_populates="client_engagement_extend")
    engagement_extend_coach = relationship("Coach", foreign_keys=[coach_id],
                                               back_populates="engagement_extend_coach")