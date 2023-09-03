from sqlalchemy import text
from sqlalchemy.orm import joinedload

from backend.libs.database import db
from backend.libs.fcm.new_fcm.android_fcm_message import AndroidFcmMessage
from backend.libs.fcm.new_fcm.ios_fcm_message import IosFcmMessage, NewIosFcmMessage
from backend.models.users import User

from backend.models.order import Order

def get_new_order_targets(order_idx, order_public):
    result = []
    if order_public == Order.ORDER_PUBLIC_CLUB:
        sql = """
                       select * from (SELECT u.* FROM kook_order o 
                       LEFT JOIN kook_order_club_designation d ON (o.idx = d.order_idx) 
                       LEFT JOIN kook_clubs c ON (d.club_idx = c.idx) 
                       LEFT JOIN kook_users u ON (c.master_idx = u.idx) 
                       WHERE o.idx = :order_idx UNION 
                       SELECT u.* FROM kook_order o 
                       LEFT JOIN kook_order_club_designation d ON ( o.idx = d.order_idx )
                       LEFT JOIN kook_user_club_relations r ON ( d.club_idx = r.club_idx AND r.deleted_at IS NULL )
                       LEFT JOIN kook_users u ON ( r.user_idx = u.idx )
                       where o.idx = :order_idx) u 
                       where {};
            """
    elif order_public == Order.ORDER_PUBLIC_RESERVED:
        sql = """
                       select u.* from kook_order o 
                       left join kook_order_user_designation d on o.idx = d.order_idx 
                       left join kook_users u on d.user_idx = u.idx 
                       where o.idx=:order_idx AND {};
            """
    else:
        sql = """
                       select u.* from kook_users as u 
                       left join kook_user_interest_address as uia on u.idx = uia.user_idx 
                       left join kook_address_relation as ar 
                       on uia.addr_idx = ar.interest_idx left join kook_order as o 
                       on ar.order_addr_idx = o.work_address_idx 
                       where o.idx=:order_idx AND {};
            """

    androids = ("u.push_version=2 AND (u.device_type = 2 OR u.device_type IS NULL)", AndroidFcmMessage)
    olds = ("u.push_version=1 AND (u.device_type IN('1', '2') OR u.device_type IS NULL)", IosFcmMessage)
    old_ios = ("u.push_version=2 AND u.device_type = 1", IosFcmMessage)
    new_ios = ("u.push_version=3 AND u.device_type = 1 ", NewIosFcmMessage)

    for item in [androids, olds, old_ios, new_ios]:
        result.append((db.session.query(User).from_statement(text(sql.format(item[0]))) \
            .params(order_idx=order_idx) \
            .options(joinedload(User.main_interest_address)).all(), item[1]))
    return result
