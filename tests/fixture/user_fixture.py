import pytest

from backend.libs.database import db
from tests.util.user import UserFactory
from tests.util.util import json_to_dict, get_default_header

user_json = {
    'phone' : '01022380476',
    'passwd' : 'jsw0711',
}

@pytest.fixture
def user_factory():
    return UserFactory()

@pytest.fixture
def user_key(client):
    response = client.post('/v1/users/login', json=user_json, headers=get_default_header())
    result = json_to_dict(response.data)
    return result.get('session_key')
