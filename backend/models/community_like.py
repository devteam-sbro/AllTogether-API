from backend.libs.database import db

class CommunityLike(db.Model):
    __tablename__ = 't_community_like'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    community_id = db.Column(db.Integer, nullable=False)
    add_time = db.Column(db.DateTime(timezone='Asia/Seoul'), nullable=False)

    @property
    def json(self):
        json = {
            'uid': self.uid,
            'user_id': self.user_id,
            'community_id': self.community_id,
            'add_time': self.add_time,
        }
        return json
    # required parameters on request
    def update_column(self, column, value):
        setattr(self, column, value)


