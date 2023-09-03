from backend.libs.decorators import run_async
from pyfcm import FCMNotification
from backend.libs.logger import create_temp_log, fill_temp_log


class KookFcmHelper:
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

    def __init__(self, api_key):
        self.fcm = FCMNotification(api_key=api_key)

    @run_async
    def send_preset(self, device_id, device_type, message_code,
                    message_body, start_push_idx=0, end_push_idx=0, log=True):
        if device_type == 1:
            # iOS FCM
            fcm_params = {"message_title": "Kook",
                          "message_body": message_body if message_code == 0 else self.MESSAGE_PRESET[message_code],
                          "sound": "4p¯.m4a", "timeout": 1}
        else:
            # Android FCM
            fcm_params = {"data_message": {
                "tag": message_code,
                "title": message_body if message_code == 0 else self.MESSAGE_PRESET[message_code],
                "message": message_body, "start_push_idx": start_push_idx, "end_push_idx": end_push_idx}, "timeout": 1}

        if type(device_id) == list:
            # Multiple device id
            fcm_params["registration_ids"] = self.fcm.clean_registration_ids(device_id)
            fill_temp_log(create_temp_log('fcm send preset - list'), 'input : {} \nfired : {}'.format(','.join(device_id), ','.join(fcm_params["registration_ids"])))
            result = self.fcm.notify_multiple_devices(**fcm_params)
        else:
            # Single device id
            fcm_params["registration_id"] = device_id
            result = self.fcm.notify_single_device(**fcm_params)

        if log:
            msg = "[FCM SEND - {0}]\n{1} {2}\n{3}".format(message_code,
                                                          device_type,
                                                          device_id, result)
            print(msg)
            fill_temp_log(create_temp_log('fcm send preset'), msg)

