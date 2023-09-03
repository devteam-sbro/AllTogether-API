import uuid
from datetime import datetime, timedelta

import requests
from random import randint
from backend import app
from backend.libs.database import db
from backend.models.sms_auth import SmsAuth
from backend.models.users import User


class SmsValidator:

    def __init__(self, recipient):
        self.recipient = recipient

    def make_auth_set(self):
        user = db.session.query(User).filter_by(phone=self.recipient).one_or_none()
        auth = SmsAuth(**{'user_id': user.idx if user is not None else None,
                          'auth_value': ''.join([str(randint(0, 9)) for x in range(0, 6)]),
                          'auth_key':uuid.uuid4(),
                          'expiration': datetime.now() +timedelta(minutes=10)}
                       )
        db.session.add(auth)
        db.session.flush()
        return auth.json


class Sms:
    HOST = 'https://api-sms.cloud.toast.com'
    APPKEY = app.config['TOAST_CLOUD_APP_KEY']

    def __init__(self, recipient):
        self.recipient = {'recipientNo': recipient}
        self.validator = SmsValidator(recipient)

    def send_sms(self, content):
        sms_result = requests.post("{host}/sms/v2.0/appKeys/{key}/sender/sms".format(host=self.HOST, key=self.APPKEY),
                                   json={
                'body': content,
                'sendNo': app.config['SMS_SENDER_NO'],
                'recipientList': [self.recipient]
            }).json()

        return sms_result

    def send_validation_sms(self):
        auth_set = self.validator.make_auth_set()
#        self.send_sms('[Kook]: {}'.format(auth_set['auth_value']))
        return auth_set


