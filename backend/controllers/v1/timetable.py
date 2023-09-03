
from flask_api import status
from flask import request

from backend.controllers.v1 import api_v1
from backend.libs.database import db
from backend.libs.decorators import login_required, with_model, route

from backend.models.timetable import TimeTable
from sqlalchemy.sql import text
import datetime


@route(app=api_v1, path='/timetable/add', methods=['POST'])
@login_required
@with_model(TimeTable.add_timetable1)
def add_timetable(user=None, data=None):

    dt = data["content"]

    for time in dt["timeList"]:
        for week in time["dayNumList"]:
            timetable = TimeTable(user_id=user.uid,
                                  lesson=dt["lesson"],
                                  teacher=dt["teacher"],
                                  day_num=week,
                                  begin_hour=time["begin_hour"],
                                  begin_minute=time["begin_minute"],
                                  end_hour=time["end_hour"],
                                  end_minute=time["end_minute"] )

            db.session.add(timetable)
            db.session.commit()

    return {'result': 0}, status.HTTP_200_OK

@route(app=api_v1, path="/timetable/list", methods=['POST'])
@login_required
def get_timetable(user=None):

    result = db.session.query(TimeTable).filter(TimeTable.user_id == user.uid).all()

    data = [r.json for r in result]
    return {"result": 0, "data": {"list": data}}, status.HTTP_200_OK

@route(app=api_v1, path="/timetable/list/today", methods=['POST'])
@login_required
def get_timetable_today(user=None):

    week_num_today = datetime.date.today().weekday()

    result = db.session.query(TimeTable).filter(TimeTable.day_num == week_num_today, TimeTable.user_id == user.uid).all()

    data = [r.json for r in result]
    return {"result": 0, "data": {"list": data}}, status.HTTP_200_OK


@route(app=api_v1, path="/timetable/list/tomorrow", methods=['POST'])
@login_required
def get_timetable_tomorrow(user=None):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    week_num_today = tomorrow.weekday()

    result = db.session.query(TimeTable).filter(TimeTable.day_num == week_num_today,
                                                TimeTable.user_id == user.uid).all()

    data = [r.json for r in result]
    return {"result": 0, "data": {"list": data}}, status.HTTP_200_OK

@route(app=api_v1, path='/timetable/update', methods=['POST'])
@login_required
def update_timetable(user=None):
    data = request.json
    dt = data["content"]
    timetable = TimeTable.query.filter_by(uid=data["uid"]).first()
    if timetable is None:
        return {'result': -1, 'msg': 'No timetable'}, status.HTTP_404_NOT_FOUND

    data = request.json

    update_sql = ""
    for k, v in dt.items():
        timetable.update_column(k, v)
    db.session.commit()
    print(update_sql)

    return {'result': 0}, status.HTTP_200_OK

@route(app=api_v1, path='/timetable/delete', methods=['POST'])
@login_required
def delete_timetable(user=None):
    data = request.json
    timetable = TimeTable.query.filter_by(uid=data["uid"]).first()
    if timetable is None:
        return {'result': -1, 'msg': 'No timetable'}, status.HTTP_404_NOT_FOUND

    db.session.delete(timetable)
    db.session.commit()

    return {'result': 0}, status.HTTP_200_OK

@route(app=api_v1, path='/timetable/deleteAll', methods=['POST'])
@login_required
def delete_all_timetable(user=None):
    timetable = TimeTable.query.filter_by(user_id=user.uid).all()
    if timetable is None:
        return {'result': -1, 'msg': 'No timetable'}, status.HTTP_404_NOT_FOUND
    for t in timetable:
        db.session.delete(t)
    db.session.commit()

    return {'result': 0}, status.HTTP_200_OK
