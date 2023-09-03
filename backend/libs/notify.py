import json
from datetime import datetime

from pytz import timezone

from backend import app
from backend.libs.database import db
from backend.libs.fcm.fcm_helper import KookFcmHelper
from backend.libs.fcm.new_fcm.message_factory import message_factory
from backend.libs.fcm.new_fcm.new_helper import get_new_order_targets
from backend.libs.logger import create_temp_log, fill_temp_log
from backend.models.address_relation import AddressRelation
from backend.models.const import Const
from backend.models.pushes import Push
from backend.models.users import User

fcm_helper = KookFcmHelper(api_key=app.config['FCM_APIKEY'])

def new_order(sender, order):
    """ FCM [1 ]

    FCMData:
        Order.json

    Args:
        order (SQLAlchemy): Order Object
    """
    msg = {'message': '{} / {}층 / {} \n{}'.format(order.json.get('work_address'),
                                                  order.json.get('work_floor'),
                                                  order.json.get('work_date'),
                                                  order.json.get('work_time')), 
           'move': 1,
           'order_idx': order.idx
           }

    relation = db.session.query(AddressRelation).filter(
        (AddressRelation.order_addr_idx == order.work_address_idx)).one()
    fill_temp_log(create_temp_log('fcm - new order -> interest address:'), relation.interest_idx)
    targets = get_new_order_targets(order.idx, order.order_public)

    for item in targets:
        item[1](fcm_helper.MESSAGE_PRESET[1], msg).send_by_tier(sender, relation, item[0])

def register_order(sender, order):
    """ FCM [2 ]

    FCMData:
        Order.json

    Args:
        order (SQLAlchemy): Order Object
    """

    print("[[ REGISTER ORDER ]]")
    worker_msg = orderer_msg = order.json
    if (order.orderer.device_type == 2 and order.orderer.push_version == 2) or order.orderer.push_version == 3:
        orderer_msg = {'message': 'Msg.',
                       'move': 2, 'order_idx': order.idx, 'user_type': 'orderer'}
    if (order.worker.device_type == 2 and order.worker.push_version == 2) or order.worker.push_version == 3:
        worker_msg = {'message': 'Msg.',
                      'move': 2, 'order_idx': order.idx, 'user_type': 'worker'}

    save_push_log(sender, order.orderer.idx, "Msg.", orderer_msg)
    if order.orderer.is_push_on(Const.PUSH_TYPE_ORDER):
        message_factory(order.orderer)("Msg.", orderer_msg).send([order.orderer.device_id])

    save_push_log(sender, order.worker.idx, "Msg", worker_msg)
    if order.worker.is_push_on(Const.PUSH_TYPE_ORDER):
        message_factory(order.worker)("Msg", worker_msg).send([order.worker.device_id])

def proceed_order(sender, order):
    """ FCM [3 ]

    FCMData:
        Order.json

    Args:
        order (SQLAlchemy): Order Object
    """
    orderer_msg = worker_msg = order.json
    if (order.orderer.device_type == 2 and order.orderer.push_version == 2) or order.orderer.push_version == 3:
        orderer_msg = {'message': 'Msg.',
                       'move': 2, 'order_idx': order.idx, 'user_type': 'orderer'}
    if (order.worker.device_type == 2 and order.worker.push_version == 2) or order.worker.push_version == 3:
        worker_msg = {'message': 'Msg.',
                      'move': 2, 'order_idx': order.idx, 'user_type': 'worker'}

    save_push_log(sender, order.orderer.idx, "Msg", orderer_msg)
    if order.orderer.is_push_on(Const.PUSH_TYPE_ORDER):
        message_factory(order.orderer)("Msg", orderer_msg).send([order.orderer.device_id])

    save_push_log(sender, order.worker.idx, "Msg", worker_msg)
    if order.worker.is_push_on(Const.PUSH_TYPE_ORDER):
        message_factory(order.worker)("Msg", worker_msg).send([order.worker.device_id])

def cancel_order(sender, order, worker, msg, user=None):
    """ FCM [4 ]

    FCMData:
        {'order_idx': 0, 'cancel_msg': "msg"}

    Args:
        order (SQLAlchemy): Order Object
        worker (SQLAlchemy): worker User Object
        msg (str): cancel message
    """
    if user and user.type == User.type_orderer:
        title = 'Msg'
    else:
        title = 'Msg'

    orderer_msg = {'message': msg,
                   'move': 2, 'order_idx': order.idx, 'user_type': 'orderer'}
    worker_msg = {'message': msg,
                   'move': 2, 'order_idx': order.idx, 'user_type': 'worker'}

    save_push_log(sender, order.orderer.idx, title, orderer_msg)
    if order.orderer.is_push_on(Const.PUSH_TYPE_ORDER):
        message_factory(order.orderer)(title, orderer_msg).send([order.orderer.device_id])

    save_push_log(sender, worker.idx, title, worker_msg)
    if worker.is_push_on(Const.PUSH_TYPE_ORDER):
        message_factory(worker)(title, worker_msg).send([worker.device_id])


def done_order(sender, order):
    """ FCM [5 ]

    FCMData:
        Order.json

    Args:
        order (SQLAlchemy): Order Object
    """

    if (order.orderer.device_type == 2 and order.orderer.push_version == 2) or order.orderer.push_version == 3:
        orderer_msg = {'message': 'Msg.',
                       'move': 2, 'order_idx': order.idx, 'user_type': 'orderer'}
    else:
        orderer_msg = order.json

    save_push_log(sender, order.orderer.idx, "Msg", orderer_msg)
    if order.orderer.is_push_on(Const.PUSH_TYPE_ORDER):
        message_factory(order.orderer)("Msg", orderer_msg).send([order.orderer.device_id])

    if (order.worker.device_type == 2 and order.worker.push_version == 2) or order.worker.push_version == 3:
        worker_msg = {'message': 'Msg.',
                      'move': 2, 'order_idx': order.idx, 'user_type': 'worker'}
    else:
        worker_msg = order.json

    save_push_log(sender, order.worker.idx, "작업이 완료되었습니다", worker_msg)
    if order.worker.is_push_on(Const.PUSH_TYPE_ORDER):
        message_factory(order.worker)("작업이 완료되었습니다", worker_msg).send([order.worker.device_id])

def userinfo_updated(user):
    """ FCM [6 ]

    FCMData:
        {}

    Args:
        user (SQLAlchemy): User Object
    """

    fcm_helper.send_preset(
        device_id=user.device_id,
        device_type=user.device_type,
        message_code=6,
        message_body={}
    )


def new_notice(users):
    """ FCM [7 ]

    FCMData:
        {}

    Args:
        users (list): User Object list
    """

    android_ids = []
    ios_ids = []
    for user in users:
        if user.device_type == user.type_device_ios:
            ios_ids.append(user.device_id)
        else:
            android_ids.append(user.device_id)

    if len(ios_ids) > 0:
        fcm_helper.send_preset(
            device_id=ios_ids,
            device_type=2,
            message_code=7,
            message_body={}
        )
    if len(android_ids) > 0:
        fcm_helper.send_preset(
            device_id=android_ids,
            device_type=1,
            message_code=7,
            message_body={}
        )


def point_charged(user, amount):
    """ FCM [8 ]

    FCMData:
        {'amount': 0}

    Args:
        user (SQLAlchemy): User Object
        amount (int): charged point amount
    """

    fcm_helper.send_preset(
        device_id=user.device_id,
        device_type=user.device_type,
        message_code=8,
        message_body={"amount": amount}
    )


def point_charged_multiple_user(users, amount):
    """ FCM [8 ]

    FCMData:
        {'amount': 0}

    Args:
        users (list): User Object list
        amount (int): charged point amount
    """

    android_ids = []
    ios_ids = []
    for user in users:
        if user.device_type == user.type_device_ios:
            ios_ids.append(user.device_id)
        else:
            android_ids.append(user.device_id)

    if len(ios_ids) > 0:
        fcm_helper.send_preset(
            device_id=ios_ids,
            device_type=2,
            message_code=8,
            message_body={"amount": amount}
        )
    if len(android_ids) > 0:
        fcm_helper.send_preset(
            device_id=android_ids,
            device_type=1,
            message_code=8,
            message_body={"amount": amount}
        )


def point_withdrawal(user, amount):
    """ FCM [9 ]

    FCMData:
        {'amount': 0}

    Args:
        user (SQLAlchemy): User Object
        amount (int): withdrawaled point amount
    """

    fcm_helper.send_preset(
        device_id=user.device_id,
        device_type=user.device_type,
        message_code=9,
        message_body={"amount": amount}
    )


def point_reject(user, point):
    """ FCM [10 ]

    FCMData:
        {'point_idx': 0, 'amount': 0}

    Args:
        user (SQLAlchemy): User Object
        point (SQLAlchemy): Point Object
    """
    msg = {"point_idx": point.idx, "amount": point.amount}

    if user.device_type == 1:
        msg = {'message': '%d Msg.' % point.amount,
               'move': 0}

    fcm_helper.send_preset(
        device_id=user.device_id,
        device_type=user.device_type,
        message_code=10,
        message_body=msg
    )

def new_chat(sender, users, chat):
    """ FCM [7 ]

    FCMData:
        {}

    Args:
        users (list): User Object list
    """
    title = chat
    body = {'message': chat, 'move': 4}
#     for user in users:
#         message_factory(user)(title, body).send([user.device_id])
    android_ids = []
    ios_ids = []
    for user in users:

        if not user.is_push_on(Const.PUSH_TYPE_BOARD):
            continue

        if user.device_type == user.type_device_ios:
            ios_ids.append(user.device_id)
        else:
            android_ids.append(user.device_id)

    message_factory(sender)(title, body).send(android_ids)
    message_factory(sender)(title, body).send(ios_ids)

def new_review(sender, review, move):
    if move == 5:
        title = 'Msg.'
    elif move == 6:
        title = 'Msg.'
    else:
        title = 'Msg.'

    body = {'message': title, 'move': move, 'idx': review}

#     users = db.session.query(User).filter((User.type == User.type_driver)).all()
#     for user in users:
#         if not user.is_push_on(Const.PUSH_TYPE_BOARD):
#             continue
#
#         message_factory(user)(title, body).send([user.device_id])

    android_ids = []
    ios_ids = []
    users = db.session.query(User).filter((User.type == User.type_driver)).all()
    for user in users:

        if not user.is_push_on(Const.PUSH_TYPE_BOARD):
            continue

        if user.device_type == user.type_device_ios:
            ios_ids.append(user.device_id)
        else:
            android_ids.append(user.device_id)

    message_factory(sender)(title, body).send(android_ids)
    message_factory(sender)(title, body).send(ios_ids)
#     if len(ios_ids) > 0:
#         KookFcmHelper.send_preset(
#             device_id=ios_ids,
#             device_type=1,
#             message_code=0,
#             message_body=body
#         )
#     if len(android_ids) > 0:
#         KookFcmHelper.send_preset(
#             device_id=android_ids,
#             device_type=1,
#             message_code=0,
#             message_body=body
#         )

def push(push_type, sender, users, title):
    android_ids = []
    ios_ids = []
    start_push_idx = None
    end_push_idx = None
    for user in users:
        end_push_idx = save_push_log(sender, user.idx, title)
        if start_push_idx is None:
            start_push_idx = end_push_idx

        if not user.is_push_on(push_type):
            continue

        if user.device_type == user.type_device_ios:
            ios_ids.append(user.device_id)
        else:
            android_ids.append(user.device_id)

    if len(ios_ids) > 0:
        fcm_helper.send_preset(
            device_id=ios_ids,
            device_type=1,
            message_code=0,
            message_body=title,
            start_push_idx=start_push_idx,
            end_push_idx=end_push_idx
        )
    if len(android_ids) > 0:
        fcm_helper.send_preset(
            device_id=android_ids,
            device_type=2,
            message_code=0,
            message_body=title,
            start_push_idx=start_push_idx,
            end_push_idx=end_push_idx
        )

def invite_club(sender, user, club):
    title = "[{}] Msg.".format(club.name)
    body = {'message': title, 'move': 3, 'club_idx': club.idx, 'club_name': club.name, 'master_idx': club.master_idx}

    save_push_log(sender, user.idx, title, body)
    message_factory(user)(title, body).send([user.device_id])

def save_push_log(sender, receiver, title, body = None):
    push_model = Push(sender_idx=sender, receiver_idx=receiver, title=title, body=json.dumps(body),
                      created_at=datetime.now(timezone('Asia/Seoul')))
    db.session.add(push_model)
    db.session.commit()

    return push_model.idx;
