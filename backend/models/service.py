from datetime import datetime

from pytz import timezone

from backend.libs.database import db



class ServiceTerm(db.Model):
    __tablename__ = 'service_term'
    version = db.Column(db.CHAR(4), primary_key=True)
    personal_info_term = db.Column(db.TEXT)
    service_term = db.Column(db.TEXT)
    marketing_term = db.Column(db.TEXT)
    register_term = db.Column(db.TEXT)
    created_at = db.Column(db.DateTime(timezone='Asia/Seoul'))


class Notice(db.Model):
    __tablename__ = 'notice'
    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(1024))
    created_at = db.Column(db.DateTime(timezone='Asia/Seoul'))

    readers = db.relationship("NoticeRead", lazy="subquery")

    @property
    def json(self):
        return {'idx': self.idx, 'content': self.content, 'title': self.title,
                'created_at': self.created_at.strftime("%y.%m.%d")}

class Banner(db.Model):
    __tablename__ = "kook_banner"
    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_url = db.Column(db.String(512), nullable=False)
    link_url = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime())

    @property
    def json(self):
        return {'image_url': self.image_url, 'link_url': self.link_url}

class Ad(db.Model):
    __tablename__ = "kook_ad"
    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_url = db.Column(db.String(512), nullable=False)
    link_url = db.Column(db.String(512), nullable=True)
    show = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone='Asia/Seoul'))

    @property
    def json(self):
        return {'image_url': self.image_url, 'link_url': self.link_url}

class AppVersion(db.Model):
    __tablename__ = 'app_version'
    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime())
    aos = db.Column(db.String(15))
    ios = db.Column(db.String(15))

class NoticeRead(db.Model):
    __tablename__ = 'notice_read'
    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notice_idx = db.Column(db.Integer, db.ForeignKey(Notice.idx), nullable=False)
    user_idx = db.Column(db.Integer, db.ForeignKey('kook_users.idx'), nullable=False)
    created_at = db.Column(db.DateTime(timezone='Asia/Seoul'))
