from flask_api import status

from backend import app
from backend.libs.decorators import route
from backend.models.service import Ad


@route(app=app, path='/ads', methods=['GET'])
def get_ads():
    ads = Ad.query.filter_by(show="SHOW").order_by(Ad.idx.desc()).all()
    return [a.json for a in ads], status.HTTP_200_OK
