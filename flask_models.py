from flask_test import db


class AuthUser(db.Model):
    __tablename__ = 'auth_user'
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String, unique=True, index=True)
    username = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    password = db.Column(db.String)
    is_active = db.Column(db.Boolean, default=True)
    is_staff = db.Column(db.Boolean, default=True)
    is_superuser = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)

    client_user = db.relationship("Client", lazy='dynamic', foreign_keys='Client.user_id', back_populates="client_user")
    answer_mapper_user = db.relationship("UserAnswerMapper", foreign_keys='UserAnswerMapper.user_id',
                                         back_populates="answer_mapper_user")

    def json(self):
        """
        Json representation of the User Profile model.
        :return:
        """
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser,
            'date_joined': self.date_joined,
            'last_login': self.last_login
        }


class Client(db.Model):
    __tablename__ = 'client_onboarding_client'
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    inactive_flag = db.Column(db.Boolean, default=False, )
    paused_flag = db.Column(db.Boolean, default=False, )
    engagement_complete = db.Column(db.Boolean, default=False, )
    minimum_number_of_invites_to_see_self_results = db.Column(db.Integer, default=5)
    minimum_number_of_people_answered_to_see_others_average = db.Column(db.Integer, default=3)
    survey_slug = db.Column(db.String, nullable=True)
    contract_duration = db.Column(db.Integer, default=180)
    # modules_id = db.Column(db.Integer)
    # coach_modules_id = db.Column(db.Integer)
    # functional_areas_id = db.Column(db.Integer)
    # areas_of_expertise_id = db.Column(db.Integer)
    # languages_id = db.Column(db.Integer)
    preferred_language_id = db.Column(db.Integer, db.ForeignKey('coach_onboarding_language.id'))
    assignedCoach_id = db.Column(db.Integer, nullable=True)
    assigned_csm_id = db.Column(db.Integer, nullable=True)
    firstName = db.Column(db.String, )
    lastName = db.Column(db.String, )
    city = db.Column(db.String, nullable=True)
    state = db.Column(db.String, nullable=True)
    country_id = db.Column(db.Integer, db.ForeignKey('coach_onboarding_country.id'))
    zipCode = db.Column(db.String, nullable=True)
    gender = db.Column(db.String, nullable=True)
    age = db.Column(db.String, nullable=True)
    highestEducation = db.Column(db.String, nullable=True)
    job_level = db.Column(db.String, nullable=True)
    job_title = db.Column(db.String, nullable=True)
    email = db.Column(db.String, )
    notes = db.Column(db.String, nullable=True)
    notes_by_client = db.Column(db.String, nullable=True)
    invalid_password_attempts = db.Column(db.Integer, default=0)
    linkedin_info_pdf = db.Column(db.String, nullable=True)
    linkedin_public_profile_url = db.Column(db.String, nullable=True)
    title_id = db.Column(db.Integer, nullable=True, )
    number_of_people_reporting_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_numberofpeoplereporting.id'))
    number_of_people_interacting_id = db.Column(db.Integer, nullable=True)
    push_notification_device_token = db.Column(db.String, nullable=True)
    allow_push_notification_and_disable_email = db.Column(db.Boolean, default=False)
    professional_development_question = db.Column(db.String, nullable=True, )
    your_role = db.Column(db.String, nullable=True, )
    did_you_have_a_coach = db.Column(db.String, nullable=True, )
    coaching_pairing_preference = \
        db.Column(db.String, nullable=True, )
    anything_else = db.Column(db.String, nullable=True, )
    email_to_sign_in_1 = db.Column(db.Boolean, default=False)
    email_to_sign_in_2 = db.Column(db.Boolean, default=False)
    career_and_vision_questions_answered = db.Column(db.Boolean, default=False)
    exercise_id = db.Column(db.Integer, nullable=True, )
    is_hr_person = db.Column(db.Boolean, default=False)
    additional_comments = db.Column(db.String, nullable=True)
    coach_payment_start_date = db.Column(db.DateTime, nullable=True)
    reason_for_coach_pairing = db.Column(db.String, nullable=True)
    client_drop_date = db.Column(db.DateTime, nullable=True)
    show_conference_call_feedback = db.Column(db.Boolean, default=False)
    timezone = db.Column(db.String, nullable=True, default="America/Los_Angeles")
    plan = db.Column(db.String, nullable=True)
    company_id = db.Column(db.Integer)
    has_materials = db.Column(db.Boolean, default=False, )
    client_manager_exercise_slug = db.Column(db.String, nullable=True, )
    show_reassessment_by_csm = db.Column(db.Boolean, default=False, )
    reassessment_triggered_on = db.Column(db.DateTime, nullable=True)
    show_manager_result = db.Column(db.Boolean, default=False, )
    show_invitee_comments = db.Column(db.Boolean, default=False, )
    show_invitee_additional_feedback = db.Column(db.Boolean, default=False, )
    use_new_assessment_view = db.Column(db.Boolean, default=False, )
    is_test_account = db.Column(db.Boolean, default=False, )
    send_manager_feedback = db.Column(db.Boolean, default=False, )
    manager_feedback_frequency = db.Column(db.Integer, default=6, )
    should_view_assessment_results = db.Column(db.Boolean, default=False, )
    group_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_clientgroup.id'))
    impact_report_file = db.Column(db.String, nullable=True)
    import_report_s3_link = db.Column(db.String, nullable=True)
    video_test_fail_email_sent_on = db.Column(db.DateTime, nullable=True)
    uses_saml_login = db.Column(db.Boolean, default=False, )
    uses_new_dashboard = db.Column(db.Boolean, default=False, )
    saml_login_idp_id = db.Column(db.String, nullable=True, )
    company_sale_id = db.Column(db.Integer, nullable=True)
    video_chat_url = db.Column(db.String, nullable=True, )
    is_deactivated = db.Column(db.Boolean, default=False, )
    should_open_reassessment_section = db.Column(db.Boolean, default=True)
    is_trial = db.Column(db.Boolean, default=False, )
    assessment_only_plus_two = db.Column(db.Boolean, default=False, )

    client_group = db.relationship("ClientGroup", foreign_keys=[group_id], back_populates="client_group")
    client_user = db.relationship("AuthUser", foreign_keys=[user_id], back_populates="client_user")
    client_numberofpeoplereporting = db.relationship("NumberofPeopleReporting",
                                                     foreign_keys=[number_of_people_reporting_id],
                                                     back_populates="client_numberofpeoplereporting")

    client_country = db.relationship("Country",
                                     foreign_keys=[country_id], back_populates="client_country")

    client_language = db.relationship("Language",
                                      foreign_keys=[preferred_language_id], back_populates="client_language")

    client_manager_three_way_call = db.relationship("ManagerThreeWayCallSession", lazy='dynamic',
                                                    foreign_keys='ManagerThreeWayCallSession.client_id',
                                                    back_populates="client_manager_three_way_call")

    client_extra_info = db.relationship("ClientExtraInfo", lazy='dynamic',
                                        foreign_keys='ClientExtraInfo.client_id', back_populates="client_extra_info")

    focus_area_client = db.relationship("FocusAreaSkillSelection", foreign_keys='FocusAreaSkillSelection.client_id',
                                        back_populates="focus_area_client")

    client_engagement_tracker = db.relationship("EngagementTracker", foreign_keys='EngagementTracker.client_id', lazy='dynamic',
                                                back_populates="client_engagement_tracker")
    client_contract_info = db.relationship("ClientContractInfo", foreign_keys='ClientContractInfo.client_id', lazy='dynamic',
                                           back_populates="client_contract_info")
    client_engagement_extend = db.relationship("EngagementExtendInfo",
                                               foreign_keys='EngagementExtendInfo.client_id', lazy='dynamic',
                                               back_populates="client_engagement_extend")

    client_notes = db.relationship("Notes", foreign_keys='Notes.client_id', lazy='dynamic',
                                     back_populates="client_notes")

    hr_partner = db.relationship("HRPartnerMapping", foreign_keys='HRPartnerMapping.client_id', lazy='dynamic',
                                     back_populates="hr_partner")


class ClientGroup(db.Model):
    __tablename__ = 'client_onboarding_clientgroup'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)
    display_name = db.Column(db.String, nullable=True)
    take_assessment_only = db.Column(db.Boolean, default=False)

    client_group = db.relationship("Client", lazy='dynamic', foreign_keys='Client.group_id',
                                   back_populates="client_group")


class Coach(db.Model):
    __tablename__ = 'coach_onboarding_coach'
    id = db.Column(db.Integer, primary_key=True, index=True)
    firstName = db.Column(db.String)
    lastName = db.Column(db.String)
    company_id = db.Column(db.Integer)
    is_test_account = db.Column(db.Boolean)
    inactive_flag = db.Column(db.Boolean)
    is_external_coach = db.Column(db.Boolean)

    engagement_tracker_coach = db.relationship('EngagementTracker', foreign_keys='EngagementTracker.coach_id',
                                               back_populates="engagement_tracker_coach")
    engagement_extend_coach = db.relationship('EngagementExtendInfo', foreign_keys='EngagementExtendInfo.coach_id',
                                              back_populates="engagement_extend_coach")


class Notes(db.Model):
    __tablename__ = 'enterprice_dashboard_notes'
    id = db.Column(db.Integer, primary_key=True, index=True)
    notes = db.Column(db.String)
    client_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_client.id'))
    client_notes = db.relationship("Client",
                                        foreign_keys=[client_id], back_populates="client_notes")

class HRPartnerMapping(db.Model):
    __tablename__ = 'enterprice_dashboard_hrpartnermapping'
    id = db.Column(db.Integer, primary_key=True, index=True)
    hr_first_name = db.Column(db.String)
    hr_last_name = db.Column(db.String)

    client_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_client.id'))
    hr_partner = db.relationship("Client",
                                        foreign_keys=[client_id], back_populates="hr_partner")


class NumberofPeopleReporting(db.Model):
    __tablename__ = 'client_onboarding_numberofpeoplereporting'
    id = db.Column(db.Integer, primary_key=True, index=True)
    option = db.Column(db.String)

    client_numberofpeoplereporting = db.relationship("Client", lazy='dynamic',
                                                     foreign_keys='Client.number_of_people_reporting_id',
                                                     back_populates="client_numberofpeoplereporting")


class Country(db.Model):
    __tablename__ = 'coach_onboarding_country'
    id = db.Column(db.Integer, primary_key=True, index=True)
    country = db.Column(db.String)

    client_country = db.relationship("Client", lazy='dynamic',
                                     foreign_keys='Client.country_id', back_populates="client_country")


class Language(db.Model):
    __tablename__ = 'coach_onboarding_language'
    id = db.Column(db.Integer, primary_key=True, index=True)
    language = db.Column(db.String)

    client_language = db.relationship("Client", lazy='dynamic',
                                      foreign_keys='Client.preferred_language_id', back_populates="client_language")


class ManagerThreeWayCallSession(db.Model):
    __tablename__ = 'chat_managerthreewaycallsession'
    id = db.Column(db.Integer, primary_key=True, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_client.id'))

    client_manager_three_way_call = db.relationship("Client",
                                                    foreign_keys=[client_id],
                                                    back_populates="client_manager_three_way_call")


class ClientExtraInfo(db.Model):
    __tablename__ = 'client_onboarding_clientextrainfo'
    id = db.Column(db.Integer, primary_key=True, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_client.id'))
    data = db.Column(db.JSON)

    client_extra_info = db.relationship("Client",
                                        foreign_keys=[client_id], back_populates="client_extra_info")


class UserAnswerMapper(db.Model):
    __tablename__ = 'exercise_useranswermapper'
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    answered_by_id = db.Column(db.Integer, db.ForeignKey('exercise_peopleansweringexercise.id'))
    is_reassessment = db.Column(db.Boolean)
    answered = db.Column(db.Boolean)

    answer_mapper_user = db.relationship("AuthUser", foreign_keys=[user_id],
                                         back_populates="answer_mapper_user")
    answer_mapper_answered_by = db.relationship("PeopleAnsweringExercise",
                                                foreign_keys=[answered_by_id],
                                                back_populates="answer_mapper_answered_by")


class PeopleAnsweringExercise(db.Model):
    __tablename__ = 'exercise_peopleansweringexercise'
    id = db.Column(db.Integer, primary_key=True, index=True)
    related_as = db.Column(db.String)
    answer_mapper_answered_by = db.relationship("UserAnswerMapper",
                                                foreign_keys='UserAnswerMapper.answered_by_id',
                                                back_populates="answer_mapper_answered_by")


class FocusAreaSkillSelection(db.Model):
    __tablename__ = 'client_onboarding_focusareaskillselection'
    id = db.Column(db.Integer, primary_key=True, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_client.id'))
    focus_area_skill_id = db.Column(db.Integer, db.ForeignKey('coach_dashboard_skill.id'))

    focus_area_client = db.relationship("Client", foreign_keys=[client_id],
                                        back_populates="focus_area_client")
    focus_area_skill = db.relationship("Skill",
                                       foreign_keys=[focus_area_skill_id],
                                       back_populates="focus_area_skill")


class Skill(db.Model):
    __tablename__ = 'coach_dashboard_skill'
    id = db.Column(db.Integer, primary_key=True, index=True)
    skillName = db.Column(db.String)
    description = db.Column(db.String)

    focus_area_skill = db.relationship("FocusAreaSkillSelection",
                                       foreign_keys='FocusAreaSkillSelection.focus_area_skill_id',
                                       back_populates="focus_area_skill")


class EngagementTracker(db.Model):
    __tablename__ = 'client_onboarding_engagementtracker'
    id = db.Column(db.Integer, primary_key=True, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_client.id'))
    coach_id = db.Column(db.Integer, db.ForeignKey('coach_onboarding_coach.id'))
    duration = db.Column(db.Integer, default=180)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    total_sessions = db.Column(db.Integer, default=12)
    total_three_way_sessions = db.Column(db.Integer, default=0)

    client_engagement_tracker = db.relationship("Client", foreign_keys=[client_id],
                                                back_populates="client_engagement_tracker")
    engagement_tracker_coach = db.relationship("Coach", foreign_keys=[coach_id],
                                               back_populates="engagement_tracker_coach")


class ClientContractInfo(db.Model):
    __tablename__ = 'client_onboarding_clientcontractinfo'
    id = db.Column(db.Integer, primary_key=True, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_client.id'))
    duration = db.Column(db.Integer, default=0)
    duration_in_months = db.Column(db.Float, default=0)
    session_num = db.Column(db.Integer, default=0)
    three_way_session_num = db.Column(db.Integer, default=0)
    session_frequency = db.Column(db.Integer, default=0)
    session_length = db.Column(db.Integer, default=0)

    client_contract_info = db.relationship("Client", foreign_keys=[client_id],
                                           back_populates="client_contract_info")


class EngagementExtendInfo(db.Model):
    __tablename__ = 'client_onboarding_engagementextendinfo'
    id = db.Column(db.Integer, primary_key=True, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_client.id'))
    coach_id = db.Column(db.Integer, db.ForeignKey('coach_onboarding_coach.id'))
    extended_on = db.Column(db.DateTime)
    extended_duration = db.Column(db.Integer, default=0)
    should_extend_sessions = db.Column(db.Boolean, default=True)
    extended_sessions = db.Column(db.Integer, default=0)
    extended_three_way_sessions = db.Column(db.Integer, default=0)
    is_paid = db.Column(db.Boolean, default=True)

    client_engagement_extend = db.relationship("Client", foreign_keys=[client_id],
                                               back_populates="client_engagement_extend")
    engagement_extend_coach = db.relationship("Coach", foreign_keys=[coach_id],
                                              back_populates="engagement_extend_coach")
