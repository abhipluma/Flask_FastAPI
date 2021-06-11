from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy


# creates Flask object
app = Flask(__name__)  # Flask app instance initiated
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pluma_dev:pluma_dev@localhost:5432/new_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)


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
    city = db.Column(db.String,  nullable=True)
    state = db.Column(db.String,  nullable=True)
    country_id = db.Column(db.Integer, db.ForeignKey('coach_onboarding_country.id'))
    zipCode = db.Column(db.String,  nullable=True)
    gender = db.Column(db.String, nullable=True)
    age = db.Column(db.String,  nullable=True)
    highestEducation = db.Column(db.String,  nullable=True)
    job_level = db.Column(db.String,  nullable=True)
    job_title = db.Column(db.String, nullable=True)
    email = db.Column(db.String, )
    notes = db.Column(db.String, nullable=True)
    notes_by_client = db.Column(db.String, nullable=True)
    invalid_password_attempts = db.Column(db.Integer, default=0)
    linkedin_info_pdf = db.Column(db.String, nullable=True)
    linkedin_public_profile_url = db.Column(db.String, nullable=True)
    title_id = db.Column(db.Integer, nullable=True,)
    number_of_people_reporting_id = db.Column(db.Integer, db.ForeignKey('client_onboarding_numberofpeoplereporting.id'))
    number_of_people_interacting_id = db.Column(db.Integer, nullable=True)
    push_notification_device_token = db.Column(db.String, nullable=True)
    allow_push_notification_and_disable_email = db.Column(db.Boolean, default=False)
    professional_development_question = db.Column(db.String, nullable=True,)
    your_role = db.Column(db.String, nullable=True,)
    did_you_have_a_coach = db.Column(db.String, nullable=True,)
    coaching_pairing_preference = \
        db.Column(db.String, nullable=True,)
    anything_else = db.Column(db.String, nullable=True,)
    email_to_sign_in_1 = db.Column(db.Boolean, default=False)
    email_to_sign_in_2 = db.Column(db.Boolean, default=False)
    career_and_vision_questions_answered = db.Column(db.Boolean, default=False)
    exercise_id = db.Column(db.Integer, nullable=True,)
    is_hr_person = db.Column(db.Boolean, default=False)
    additional_comments = db.Column(db.String, nullable=True)
    coach_payment_start_date = db.Column(db.DateTime, nullable=True)
    reason_for_coach_pairing = db.Column(db.String, nullable=True)
    client_drop_date = db.Column(db.DateTime, nullable=True)
    show_conference_call_feedback = db.Column(db.Boolean, default=False)
    timezone = db.Column(db.String, nullable=True, default="America/Los_Angeles")
    plan = db.Column(db.String,  nullable=True)
    company_id = db.Column(db.Integer)
    has_materials = db.Column(db.Boolean, default=False, )
    client_manager_exercise_slug = db.Column(db.String, nullable=True,)
    show_reassessment_by_csm = db.Column(db.Boolean, default=False,)
    reassessment_triggered_on = db.Column(db.DateTime, nullable=True)
    show_manager_result = db.Column(db.Boolean, default=False,)
    show_invitee_comments = db.Column(db.Boolean, default=False,)
    show_invitee_additional_feedback = db.Column(db.Boolean, default=False,)
    use_new_assessment_view = db.Column(db.Boolean, default=False,)
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
    saml_login_idp_id = db.Column(db.String,  nullable=True,)
    company_sale_id = db.Column(db.Integer, nullable=True)
    video_chat_url = db.Column(db.String, nullable=True, )
    is_deactivated = db.Column(db.Boolean, default=False, )
    should_open_reassessment_section = db.Column(db.Boolean, default=True)
    is_trial = db.Column(db.Boolean, default=False, )
    assessment_only_plus_two = db.Column(db.Boolean, default=False, )

    client_group = db.relationship("ClientGroup", foreign_keys=[group_id],back_populates="client_group")
    client_user = db.relationship("AuthUser", foreign_keys=[user_id],back_populates="client_user")
    client_numberofpeoplereporting = db.relationship("NumberofPeopleReporting", 
    foreign_keys=[number_of_people_reporting_id],back_populates="client_numberofpeoplereporting")

    client_country = db.relationship("Country", 
    foreign_keys=[country_id],back_populates="client_country")

    client_language = db.relationship("Language", 
    foreign_keys=[preferred_language_id],back_populates="client_language")

class ClientGroup(db.Model):
    __tablename__ = 'client_onboarding_clientgroup'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)
    display_name = db.Column(db.String, nullable=True)
    take_assessment_only = db.Column(db.Boolean, default=False)

    client_group = db.relationship("Client", lazy='dynamic', foreign_keys='Client.group_id', back_populates="client_group")
    

class Coach(db.Model):
    __tablename__ = 'coach_onboarding_coach'
    id = db.Column(db.Integer, primary_key=True, index=True)
    company_id = db.Column(db.Integer)
    is_test_account = db.Column(db.Boolean)
    inactive_flag = db.Column(db.Boolean)
    is_external_coach = db.Column(db.Boolean)

class Notes(db.Model):
    __tablename__ = 'enterprice_dashboard_notes'
    id = db.Column(db.Integer, primary_key=True, index=True)
    notes = db.Column(db.String)
    client_id = db.Column(db.Integer)

class HRPartnerMapping(db.Model):
    __tablename__ = 'enterprice_dashboard_hrpartnermapping'
    id = db.Column(db.Integer, primary_key=True, index=True)
    client_id = db.Column(db.Integer)
    hr_first_name = db.Column(db.String)
    hr_last_name = db.Column(db.String)

class NumberofPeopleReporting(db.Model):
    __tablename__ = 'client_onboarding_numberofpeoplereporting'
    id = db.Column(db.Integer, primary_key=True, index=True)
    option = db.Column(db.String)

    client_numberofpeoplereporting = db.relationship("Client", lazy='dynamic', 
    foreign_keys='Client.number_of_people_reporting_id', back_populates="client_numberofpeoplereporting")

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

@app.route("/user")
def get_user():
   users = AuthUser.query.limit(10).all()
   user_list = []
   for user in users:
      user_list.append(user.json())
   return make_response(jsonify({'users': user_list}))


@app.get("/client-metrics/active/<group_id>/")
def client_metrics(group_id):
    db_clients = db.session.query(Client, ClientGroup, AuthUser).\
    filter(Client.group_id == ClientGroup.id, Client.user_id == AuthUser.id).\
    filter(ClientGroup.take_assessment_only == False, Client.is_test_account == False, Client.group_id==group_id).limit(10).all()
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
            "notes": db.session.query(Notes).filter( Notes.client_id==client.id).first().notes 
            if db.session.query(Notes).filter( Notes.client_id==client.id).first() else '',
            "hr_partner": db.session.query(HRPartnerMapping).filter( HRPartnerMapping.client_id==client.id).first().hr_first_name
            + ' ' + db.session.query(HRPartnerMapping).filter( HRPartnerMapping.client_id==client.id).first().hr_last_name
            if db.session.query(HRPartnerMapping).filter( HRPartnerMapping.client_id==client.id).first() else '',
            "number_of_people_reporting": client.client_numberofpeoplereporting.option
            if client.client_numberofpeoplereporting else '',
            "country": client.client_country.country if client.client_country else '',
            "language": client.client_language.language if client.client_language else ''
        })
    return make_response(jsonify(data))


if __name__ == "__main__":
    app.run(debug=True)
