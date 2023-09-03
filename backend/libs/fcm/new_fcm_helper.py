from pyfcm import FCMNotification

from backend import app
from backend.libs.database import db
from backend.libs.decorators import run_async
from backend.libs.logger import fill_temp_log, create_temp_log
from backend.models.address_relation import AddressRelation
from backend.models.user_tiers.tier_util import get_push_priority


class FcmHelper:
    MessageContainer = None

    def __init__(self):
        self.fcm = FCMNotification(api_key=app.config['FCM_APIKEY'])

    @run_async
    def send_presets(self, fcm_message, log=True, wait=0):
        '''
        '''
        pass

    def make_message(self, device_ids, message_code, message_body):
        return self.MessageContainer(self.fcm, device_ids, message_code, message_body=message_body)

    def send_by_tier(self, users, order, message_code, message_body=''):
        '''
        '''
        relation = db.session.query(AddressRelation).filter((AddressRelation.order_addr_idx == order.work_address_idx)).one()
        priorities = {i:[] for i in range(1, 7)}

        for user in users:
            priorities[get_push_priority(user, relation.interest_idx)].append(user.device_id)

        @run_async
        def _send():
            for i, wait in zip(range(1, 7), [0, 2, 4, 6, 8, 10]):
                priority = priorities[i]
                if len(priority) == 0:
                   continue

                fcm_message = self.make_message(priority, message_code, message_body)
                self.send_presets(fcm_message, wait=wait)

        _send()
