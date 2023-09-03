from flask import request
from flask_api import status

from backend import app
from backend.libs.decorators import route
from backend.models.service import AppVersion


@route(app=app, path='/version', methods=['GET'])
def get_app_version():
    version = AppVersion.query.order_by(AppVersion.created_at.desc()).first()
    resp = {'aos': version.aos, 'ios': version.ios}
    return resp, status.HTTP_200_OK


@route(app=app, path='/ios_plz', methods=['GET'])
def get_ios_test():
    flg = request.args.get('flg') or 0
    return {'flg': flg}, status.HTTP_200_OK
