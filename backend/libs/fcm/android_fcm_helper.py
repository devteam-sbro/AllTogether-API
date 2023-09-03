from pyfcm import FCMNotification

from backend import app
from backend.libs.decorators import run_async
from backend.libs.fcm.fcm_helper import KookFcmHelper
from backend.libs.fcm.new_fcm_helper import FcmHelper
from backend.libs.logger import create_temp_log, fill_temp_log


class AndroidFcmMessage:
    MESSAGE_PRESET = {
        1: "Msg",
        2: "Msg.",
        3: "Msg",
        4: "Msg",
        5: "Msg",
        6: "Msg",
        7: "Msg",
        8: "Msg",
        9: "Msg",
        10: "Msg",
        11: "Msg",
        12: "Msg",
        13: "Msg"
    }

    def __init__(self, fcm, device_ids, message_code, message_body=''):
        self.fcm = fcm
        self.device_ids = self.fcm.clean_registration_ids(device_ids)
        self.message_code = message_code
        self.message_body = message_body

    def content(self):
        return {
            "data_message": {
                "title": self.MESSAGE_PRESET[self.message_code],
                "message": self.message_body
            },
            "timeout": 1,
            "registration_ids": self.device_ids
        }


class AndroidFcmHelper(FcmHelper):
    MessageContainer = AndroidFcmMessage


    def __init__(self):
        super().__init__()

    def make_log(self, fcm_message, result):
        msg = "[FCM SEND - {0}]\n{1} {2}\n{3}".format(fcm_message.message_code,
                                                      'android',
                                                      fcm_message.device_ids, result)
        print(msg)
        fill_temp_log(create_temp_log('fcm send preset - list'), msg)

    @run_async
    def send_presets(self, fcm_message, log=True, wait=0):
        if len(fcm_message.device_ids) <= 0:
            return

        result = self.fcm.notify_multiple_devices(**fcm_message.content())
        self.make_log(fcm_message, result)

