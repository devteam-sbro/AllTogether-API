from datetime import datetime

from backend.libs.database import db
from backend.models.temp_log import TempLog
from backend.models.admin_log import AdminLog


def create_temp_log(func_name, flush=False, commit=True):
    new_log = TempLog(api_name=func_name, created_at=datetime.now())
    db.session.add(new_log)

    if flush is True:
        db.session.flush()

    if commit is True:
        db.session.commit()

    return new_log


def fill_temp_log(log, res, flush=False, commit=True):
    try:
        log.response = res

        if flush is True:
            db.session.flush()

        if commit is True:
            db.session.commit()

    except:
        pass


