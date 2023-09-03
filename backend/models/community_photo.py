from backend.libs.database import db
from backend.models.community import Community

class CommunityPhoto(db.Model):
    __tablename__ = 't_community_photo'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    community_id = db.Column(db.Integer, nullable=False)
    img = db.Column(db.CHAR(255), nullable=False)
    order = db.Column(db.Integer)
    img_title = db.Column(db.CHAR(255))

    community_id = db.Column(db.Integer, db.ForeignKey(Community.uid), nullable=False)

    @property
    def json(self):
        json = {
            'uid': self.uid,
            'community_id': self.community_id,
            'img': self.img,
            'order': self.order,
            'img_title': self.img_title,
        }
        return json
    # required parameters on request
    add_community_photo = ['community_id', 'img', 'img_title']
    def update_column(self, column, value):
        setattr(self, column, value)


