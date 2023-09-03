from datetime import datetime

from backend.libs.database import db
from backend.models.admin import Admin
from backend.models.order import Order, OrderTxHistory
from backend.models.order_fee import OrderFee
from backend.models.users import User
from tests.test_pyramid.unit_tests.test_register_order_fee import mocked_order_fee
from tests.util.user import UserFactory

pytest_plugins = ('tests.fixture.db_fixture')

data = {
	"order_type":2,
	"work_date":"2019-05-22",
	"work_time":"AM 09:00",
	"work_price_type":"4",
	"work_floor":2,
	"orderer_phone":"01022380476",
	"work_place_phone":"01022380476",
	"work_address_idx":"15059",
	"work_address_detail":"Test",
	"order_updown":"2",
	"order_price":"100000",
	"order_message":"sw Test",
	"order_status":1,
}

# point_dict = {
#     'orderer': 1500,
#     'chief': 500,
#     'vice': 1000
# }


def calc_point(target, orderer, chief, vice):
    result = 0
    if target.idx == orderer.idx:
        result += 1500
    if target.idx == chief.idx:
        result += 500
    if target.idx == vice.idx:
        result += 1000
    return result


def test_order_done(session, monkeypatch):
    '''

    '''
    monkeypatch.setattr(OrderFee, 'get_order_fee_from_order', mocked_order_fee)
    monkeypatch.setattr(db, 'session', session)

    orderer = UserFactory.gen_admin_master(session=session)
    session.add(orderer)
    session.flush()

    order = Order(**data)
    order.orderer_user_id = orderer.idx
    order.refresh_work_datetime()
    order.register_order_fee()
    session.add(order)
    session.flush()

    chief, vice = order.work_address.get_chief_and_vice_users()
    orderer_admin = db.session.query(Admin).filter(
        ((Admin.role == Admin.ROLE_ORDERER) | (Admin.role == Admin.ROLE_MASTER))
        & (Admin.idx == orderer.orderer_admin_idx)).first().user

    chief_point = chief.kook_point
    vice_point = vice.kook_point
    orderer_admin_point = orderer_admin.kook_point

    tx = OrderTxHistory(order_idx=order.idx, user_idx=1,
						status_from=Order.STATUS_PROCEED,
						msg='integration test',
						created_at=datetime.now(),
						status_to=Order.STATUS_DONE)
    order.pay_for_done(tx)

    session.flush()

    assert chief_point + calc_point(chief, orderer_admin, chief, vice) == session.execute\
        ('SELECT kook_point FROM kook_users WHERE idx ={};'.format(chief.idx)).scalar()
    assert vice_point + calc_point(vice, orderer_admin, chief, vice) == session.execute\
        ('SELECT kook_point FROM kook_users WHERE idx ={};'.format(vice.idx)).scalar()
    assert orderer_admin_point + calc_point(orderer_admin, orderer_admin, chief, vice) == session.execute\
        ('SELECT kook_point FROM kook_users WHERE idx ={};'.format(orderer_admin.idx)).scalar()


