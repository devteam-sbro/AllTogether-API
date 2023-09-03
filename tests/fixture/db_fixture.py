import pytest
from backend import app

@pytest.fixture(scope='session')
def db():
    '''

    '''
    from backend.libs.database import db
    return db


@pytest.fixture('class')
def session(request, db):
    db.session.begin_nested() # SAVE POINT 생성

    def tier_down_session():
        db.session.rollback()
        db.session.close()

    request.addfinalizer(tier_down_session)
    return db.session



