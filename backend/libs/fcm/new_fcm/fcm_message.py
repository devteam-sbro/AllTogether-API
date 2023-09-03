from pyfcm import FCMNotification

from backend import app
from backend.libs import notify
from backend.libs.decorators import run_async
from backend.models.const import Const
from backend.models.user_tiers.tier_util import get_push_priority

fcm = FCMNotification(api_key=app.config['FCM_APIKEY'])

class FcmMessasge:
    fcm = fcm

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.registration_ids = []

    def format_output(self):
        return {}

    def make_log(self, result):
        pass

    @run_async
    def send(self, device_ids, wait=0):
        self.registration_ids = self.fcm.clean_registration_ids(device_ids)
        if len(self.registration_ids):
            result = self.fcm.notify_multiple_devices(**self.format_output())
#             self.make_log(result)

    def send_by_tier(self, sender, relation, users):
        priorities = {i: [] for i in range(1, 7)}

        for user in users:
            if not user.is_push_on(Const.PUSH_TYPE_ORDER):
                continue
            priorities[get_push_priority(user, relation.interest_idx)].append(user.device_id)

        for i, wait in zip(range(1, 7), [0, 2, 4, 6, 8, 10]):
            if len(priorities[i]):
                self.send(priorities[i], wait=wait)
