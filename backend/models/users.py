from datetime import datetime, timedelta

from pytz import timezone

from sqlalchemy import and_, orm

from backend.models.const import Const
from backend.libs.database import db
from backend.libs.date_helper import DateHelper
from backend.libs.hash import generate_password_hash
from backend.models.service import ServiceTerm

class User(db.Model):
    __tablename__ = 't_user'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.CHAR(255), unique=True, nullable=False)
    pwd = db.Column(db.CHAR(255), nullable=False)
    name = db.Column(db.CHAR(255), nullable=False, index=True)
    nickname = db.Column(db.CHAR(255))
    phone = db.Column(db.CHAR(255), default='', nullable=False)
    photo = db.Column(db.CHAR(255), )
    market_alarm = db.Column(db.SmallInteger, default=0)
    noti_alarm = db.Column(db.SmallInteger, default=0)
    lang_type = db.Column(db.SmallInteger, default=1)

    add_time = db.Column(db.DateTime(timezone='Asia/Seoul'), nullable=False)
    del_time = db.Column(db.DateTime(timezone='Asia/Seoul'))
    dev_type = db.Column(db.CHAR(10), nullable=False)
    dev_token = db.Column(db.CHAR(255), nullable=True)
    access_token = db.Column(db.CHAR(255), nullable=True)

    session_key = ''

    # User type
    type_orderer = 1
    type_driver = 2

    type_device_ios = 1
    type_device_aos = 2

    # required parameters on request
    add_user = ['school_id', 'email', 'pwd', 'nickname', 'phone',
                'dev_type', 'dev_token']
    login = ['email', 'pwd']
    nickcheck = ['nickname']
    updatable_column = ['pwd', 'name', 'nickname', 'photo',
                   'market_alarm', 'noti_alarm', 'lang_type',
                   'del_time', 'dev_type', 'dev_token', 'access_token']

    def update_column(self, column, value):
        setattr(self, column, value)

    @property
    def json(self):

        msg = {
            'uid': self.uid,
            'school_id': self.school_id,
            'school_name': self.school_name,
            'email': self.email,
            'pwd': self.pwd,
            'name': self.name,
            'nickname': self.nickname,
            'phone': self.phone,
            'photo': self.photo,
            'market_alarm': self.market_alarm,
            'noti_alarm': self.noti_alarm,
            'lang_type': self.lang_type,
            'add_time': self.add_time.strftime('%Y-%m-%d %H:%M:%S'),
            'del_time': self.del_time.strftime('%Y-%m-%d %H:%M:%S') if self.del_time else '',
            'dev_type': self.dev_type,
            'dev_token': self.dev_token,
            'access_token': self.access_token,
        }

        return msg

class Session(db.Model):
    __tablename__ = 'all_sessions'
    session_key = db.Column(db.CHAR(64), primary_key=True)
    user_idx = db.Column(db.Integer, db.ForeignKey(User.uid), nullable=False)
    expires_in = db.Column(db.DateTime(timezone='Asia/Seoul'), nullable=False)
    activated = db.Column(db.Integer, default=1)
    user = db.relationship("User", lazy="subquery")

    def is_expired(self):
        now = datetime.now(timezone('Asia/Seoul'))
        expires_in = self.expires_in.replace(tzinfo=timezone('Asia/Seoul'))
        if expires_in < now or self.activated == 0:
            db.session.delete(self)
            db.session.commit()
            return True
        return False

    @classmethod
    def set_session(cls, key, user):
        expires_in = datetime.now(timezone('Asia/Seoul')) + timedelta(days=365)
        session = Session(session_key=key, user_idx=user.uid,
                          expires_in=expires_in)

        db.session.add(session)
        db.session.commit()

    @classmethod
    def get_session(cls, key):
        return db.session.query(Session).get(key)
