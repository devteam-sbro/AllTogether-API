from backend.libs.fcm.new_fcm.android_fcm_message import AndroidFcmMessage
from backend.libs.fcm.new_fcm.ios_fcm_message import IosFcmMessage, NewIosFcmMessage


def message_factory(user):
    '''
    '''
    if user.device_type == 1 and user.push_version == 3:
        return NewIosFcmMessage
    if user.device_type == 2 and user.push_version == 2:
        return AndroidFcmMessage
    else:
        return IosFcmMessage
