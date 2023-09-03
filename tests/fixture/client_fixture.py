import pytest
from backend import app


@pytest.fixture(scope='module')
def client():
    return app.test_client()

