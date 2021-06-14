from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# creates Flask object
app = Flask(__name__)  # Flask app instance initiated
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pluma_dev:pluma_dev@localhost:5432/pluma_local_db1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pluma_dev:pluma_dev@localhost:5432/new_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)
