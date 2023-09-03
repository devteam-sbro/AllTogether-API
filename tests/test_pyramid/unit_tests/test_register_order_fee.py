from backend.models.order import Order
from backend.models.order_fee import OrderFee

pytest_plugins = ('tests.fixture.db_fixture')

data = {
	"order_type":2,
	"work_date":"2019-05-22",
	"work_time":"AM 09:00",
	"work_price_type":"4",
	"work_floor":2,
	"orderer_phone":"01022380476",
	"work_place_phone":"01022380476",
	"work_address_idx":"",
	"work_address_detail":"Test",
	"order_updown":"2",
	"order_price":"100000", # 10 만원
	"order_message":"sw Test",
	"order_status":1,
}

def mocked_order_fee(order):
    return OrderFee(symbol='MOCK', description='mock  order fee',
                    worker_exp='{x}*0.10 + 3000',
                    orderer_exp='{x}*0.10',
                    admin_exp='3000',
                    admin_orderer_exp='1500',
                    admin_chief_exp='500',
                    admin_vice_exp='1000',
                    happy_worker_exp='2000',
                    happy_orderer_exp='1000',
                    happy_admin_exp='1000',
                    happy_admin_orderer_exp='0',
                    happy_admin_chief_exp='0',
                    happy_admin_vice_exp='0')


def test_register_order_fee(monkeypatch):
    '''
    '''
    monkeypatch.setattr(OrderFee, 'get_order_fee_from_order', mocked_order_fee)

    order = Order(**data)
    order.register_order_fee()

    assert order.worker_fee == 13000
    assert order.orderer_fee == 10000
    assert order.admin_vice_driver_fee == 1000
    assert order.admin_chief_driver_fee == 500
    assert order.admin_orderer_fee ==1500
    return order


