from datetime import datetime, timedelta

from backend.models.order import Order
from tests.util.util import get_default_header, json_to_dict
from backend.libs.database import db

pytest_plugins = ('tests.fixture.db_fixture', 'tests.fixture.client_fixture'
                  , 'tests.fixture.user_fixture')

test_order = {
	"order_type":2,
	"work_date":"2019-05-22",
	"work_time":"AM 09:00",
	"work_price_type":"4",
	"work_floor":2,
	"orderer_phone":"01022380476",
	"work_place_phone":"01022380476",
	"work_address":"",
	"work_address_detail":"Test",
	"order_updown":"2",
	"order_price":"20000",
	"order_message":"sw Test",
	"order_status":1
}


def order_speed(client, user_key, session, monkeypatch):
    '''
    '''
    now = datetime.now()
    response = client.post('/v1/order', json=test_order, headers=get_default_header(user_key))
    result = json_to_dict(response.data)
    delay = datetime.now() - now
    assert delay < timedelta(seconds=2)
    return result.get('idx')



def test(client, user_key, session, monkeypatch):
    '''
    '''
    monkeypatch.setattr(db, 'session', session)
    monkeypatch.setattr('backend.libs.notify.fill_temp_log', lambda w=None,x=None,y=None,z=None:None)
    monkeypatch.setattr('backend.libs.notify.create_temp_log', lambda w=None,x=None,y=None,z=None:None)

    idx = order_speed(client, user_key, session, monkeypatch)
