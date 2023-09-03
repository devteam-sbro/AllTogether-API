from backend.libs.database import db
from backend.models.community import Community
from backend.models.users import User
from backend.models.school import School

class Comment(db.Model):
    __tablename__ = 't_comment'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    community_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String)
    anonym = db.Column(db.CHAR(255), nullable=False)
    parent = db.Column(db.Integer)
    add_time = db.Column(db.DateTime(timezone='Asia/Seoul'), nullable=False)

    community_id = db.Column(db.Integer, db.ForeignKey(Community.uid), nullable=False)


    @property
    def json(self):
        user = db.session.query(User).filter(User.uid == self.user_id).first()
        user_name = ""
        user_photo = ""
        school_id = 0
        school_name = ""
        if (user is not None):
            user_name = user.nickname
            user_photo = user.photo
            school = db.session.query(School).filter(School.uid == user.school_id).first()
            if (school is not None):
                school_id = school.uid
                school_name = school.name
        likeCnt = db.session.query(CommentLike).filter(CommentLike.comment_id == self.uid).count()
        json = {
            'uid': self.uid,
            'community_id': self.community_id,
            'user_id': self.user_id,
            'user_name': user_name,
            'user_photo': user_photo,
            'content': self.content,
            'anonym': self.anonym,
            'parent': self.parent,
            'school_id': school_id,
            'school_name': school_name,
            'like_cnt': likeCnt,
            'add_time': self.add_time if isinstance(self.add_time, str)  else self.add_time.strftime("%m/%d %H:%M"),
        }
        return json
    # required parameters on request
    add_comment = ['community_id', 'content', 'anonym', 'parent']
    def update_column(self, column, value):
        setattr(self, column, value)

class CommentLike(db.Model):
    __tablename__ = 't_comment_like'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    add_time = db.Column(db.DateTime(timezone='Asia/Seoul'), nullable=False)

    @property
    def json(self):
        json = {
            'uid': self.uid,
            'comment_id': self.comment_id,
            'user_id': self.user_id,
            'add_time': self.add_time,
        }
        return json
    # required parameters on request
    add_comment_like = ['comment_id']
    def update_column(self, column, value):
        setattr(self, column, value)

class CommentScrap(db.Model):
    __tablename__ = 't_comment_scrap'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    add_time = db.Column(db.DateTime(timezone='Asia/Seoul'), nullable=False)

    @property
    def json(self):
        json = {
            'uid': self.uid,
            'comment_id': self.comment_id,
            'user_id': self.user_id,
            'add_time': self.add_time,
        }
        return json
    # required parameters on request
    add_comment_like = ['comment_id']
    def update_column(self, column, value):
        setattr(self, column, value)