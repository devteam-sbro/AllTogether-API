from datetime import datetime, timedelta

from pytz import timezone

from sqlalchemy import and_, orm

from backend.models.const import Const
from backend.libs.database import db
from backend.libs.date_helper import DateHelper
from backend.libs.hash import generate_password_hash
from backend.models.service import ServiceTerm
from backend.models.users import User

class School(db.Model):
    __tablename__ = 't_school'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.CHAR(255), nullable=False)
    email = db.Column(db.CHAR(255), unique=True, nullable=False)

    @property
    def json(self):
        json = {
            'uid': self.uid,
            'name': self.name,
            'email': self.email,
        }
        return json