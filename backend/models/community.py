from backend.libs.database import db
from backend.models.users import User
import json
class Community(db.Model):
    __tablename__ = 't_community'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey(User.uid), nullable=False)
    title = db.Column(db.CHAR(255), nullable=False)
    content = db.Column(db.String)
    anonym = db.Column(db.CHAR(255), nullable=False)
    add_time = db.Column(db.DateTime(timezone='Asia/Seoul'), nullable=False)

    comments = db.relationship("Comment", backref="t_community", lazy="subquery")
    photos = db.relationship("CommunityPhoto", backref="t_community", lazy="subquery")

    @property
    def json(self):
        user = db.session.query(User).filter(User.uid == self.user_id).first()
        user_name = ""
        user_photo = ""
        if (user is not None):
            user_name = user.nickname
            user_photo = user.photo

        # for a in self.comments:
        #     if(a.add_time is not None):
        #         a.add_time = a.add_time.strftime('%Y-%m-%d %H:%M:%S')
        # ret = [a.json for a in self.comments]
        json1 = {
            'uid': self.uid,
            'user_id': self.user_id,
            'user_name': user_name,
            'user_photo': user_photo,
            'title': self.title,
            'content': self.content,
            'anonym': self.anonym,
            'add_time': self.add_time if isinstance(self.add_time, str)  else self.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            # 'comments': json.loads(json.dumps(ret)),
            'comments': [],
            'photos': json.loads(json.dumps([a.json for a in self.photos])),
        }
        return json1

    # required parameters on request
    add_community = ['title', 'content', 'anonym', 'photos']
    def update_column(self, column, value):
        setattr(self, column, value)
