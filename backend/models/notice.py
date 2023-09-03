from backend.libs.database import db
from backend.models.community import Community

class Notice(db.Model):
    __tablename__ = 't_notice'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String)
    content = db.Column(db.String)
    community_id = db.Column(db.Integer, nullable=False)
    add_time = db.Column(db.DateTime(timezone='Asia/Seoul'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    @property
    def json(self):
        json = {
            'uid': self.uid,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'community_id': self.community_id,
            'add_time': self.add_time if isinstance(self.add_time, str)  else self.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            'user_id': self.user_id,
        }
        return json
    # required parameters on request
    add_notice = ['type', 'title', 'content', 'community_id', 'user_id']
    def update_column(self, column, value):
        setattr(self, column, value)

class NoticeStatus(db.Model):
    __tablename__ = 't_notice_status'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.uid'), nullable=False)
    notice_id = db.Column(db.Integer, db.ForeignKey(Notice.uid), nullable=False)
    # created_at = db.Column(db.DateTime(timezone='Asia/Seoul'))