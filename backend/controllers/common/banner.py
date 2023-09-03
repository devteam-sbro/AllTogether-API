from flask_api import status

from backend import app
from backend.libs.decorators import route
from backend.models.service import Banner


@route(app=app, path='/banners', methods=['GET'])
def get_banners():
    banners = Banner.query.order_by(Banner.idx.desc()).limit(10).all()
    return [b.json for b in banners], status.HTTP_200_OK
