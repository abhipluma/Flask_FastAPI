from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import pandas as pd
from sqlalchemy import desc

from export_column import columns_map

# creates Flask object
app = Flask(__name__)  # Flask app instance initiated
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pluma_dev:pluma_dev@localhost:5432/pluma_local_db1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pluma_dev:pluma_dev@localhost:5432/new_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)
