from datetime import datetime
from random import randint

from admin.models.admin import Admin
from backend.models.users import User


class UserHelper:

    @classmethod
    def random_phone_number(cls):
        return '010{}'.format(''.join([str(randint(0, 9)) for _ in range(0, 8)]))



class UserFactory:

    @classmethod
    def gen_driver(cls, session=None):
        user = User(phone='09012345656',
                    passwd='abc', username='드라이버', nickname='드라이버', device_id='abc',
                    type=User.type_driver, created=datetime.now(), term_version='v1.0')
        user.set_tier('Bronze')

        if session:
            session.add(user)
            session.flush()

        return user

    @classmethod
    def gen_admin_master(cls, session):
        user = User(idx=998989, phone=UserHelper.random_phone_number(),
             orderer_admin_idx=1, passwd='abc', username='마스타', nickname='마스타', device_id='abc',
             type=User.type_driver, created=datetime.now(), term_version='v1.0')

        session.add(user)
        session.flush()

        admin = Admin(role='Master', user_idx=user.idx)

        session.add(admin)
        session.flush()

        return user

    @classmethod
    def gen_admin_orderer(cls, session=None):
        pass


