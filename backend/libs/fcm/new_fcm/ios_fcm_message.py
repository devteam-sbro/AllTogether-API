from backend.libs.fcm.new_fcm.fcm_message import FcmMessasge
from backend.libs.logger import create_temp_log, fill_temp_log


class IosFcmMessage(FcmMessasge):

    def __init__(self, title, body):
        super().__init__(title, body)

    def format_output(self):
        return {
            "message_title": "Kook",
            "message_body": self.title,
            "sound": "4p¯.m4a",
            "timeout": 1,
            "registration_ids": self.registration_ids
        }

    def make_log(self, result):
        msg = 'Old Ios - FCM send: \n{title}-{body} \n{result}'.format(title=self.title, body=self.body, result=result)
        print(msg)
        fill_temp_log(create_temp_log('fcm send'), msg)


class NewIosFcmMessage(FcmMessasge):

    def __init__(self, title, body):
        super().__init__(title, body)

    def format_output(self):
        body = self.body.get('message') if isinstance(self.body, dict) else self.body
        return {
            "message_title": self.title,
            "message_body": body,
            "sound": "4p¯.m4a",
            "timeout": 1,
            "registration_ids": self.registration_ids
        }

    def make_log(self, result):
        msg = 'New Ios - FCM send: \n{title}-{body} \n{result}'.format(title=self.title, body=self.body, result=result)
        print(msg)
        fill_temp_log(create_temp_log('fcm send'), msg)
