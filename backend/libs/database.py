# Use this import format
from flask_sqlalchemy import SQLAlchemy

from backend import app

db = SQLAlchemy(app, session_options={'autocommit': False, 'autoflush': False})
