
from flask_api import status
from flask import request

from backend.controllers.v1 import api_v1
from backend.libs.database import db
from backend.libs.decorators import login_required, with_model, route

from backend.models.notice import Notice, NoticeStatus
from sqlalchemy.sql import text
import datetime
from sqlalchemy import and_,or_


@route(app=api_v1, path='/notice/my', methods=['POST'])
@login_required
def getMyNotice(user=None):
    page = request.json["page"]
    totalNotice = Notice.query.filter(
        and_(Notice.type == 0,
             or_(Notice.user_id == 0,
             Notice.user_id == user.uid))
    ).order_by(Notice.add_time.desc())

    notices = Notice.query.filter(
        and_(Notice.type == 0,
             or_(Notice.user_id == 0,
             Notice.user_id == user.uid))
    ).order_by(Notice.add_time.desc()).limit(10).all()

    totalCnt = totalNotice.count()
    isLast = page >= -(-totalCnt // 10) - 1

    ret = []
    for r in notices:
        j = r.json
        j["isRead"] = NoticeStatus.query.filter(and_(NoticeStatus.user_id == user.uid, NoticeStatus.notice_id == r.uid)
                                                ).count()
        ret.append(j)
    return {"result": 0,
            "data": {
                "total_count": totalCnt,
                "is_last": isLast,
                "list": ret
            }}, status.HTTP_200_OK

@route(app=api_v1, path='/notice/admin', methods=['POST'])
@login_required
def getAdminNotice(user=None):
    page = request.json["page"]
    totalNotice = Notice.query.filter(
        and_(Notice.type == 1,
             or_(Notice.user_id == 0,
             Notice.user_id == user.uid))
    ).order_by(Notice.add_time.desc())

    notices = Notice.query.filter(
        and_(Notice.type == 1,
             or_(Notice.user_id == 0,
             Notice.user_id == user.uid))
    ).order_by(Notice.add_time.desc()).limit(10).all()

    totalCnt = totalNotice.count()
    isLast = page >= -(-totalCnt // 10) - 1

    ret = []
    for r in notices:
        j = r.json
        j["isRead"] = NoticeStatus.query.filter(and_(NoticeStatus.user_id == user.uid, NoticeStatus.notice_id == r.uid)
                                                ).count()
        ret.append(j)
    return {"result": 0,
            "data": {
                "total_count": totalCnt,
                "is_last": isLast,
                "list": ret
            }}, status.HTTP_200_OK

@route(app=api_v1, path='/notice/read', methods=['POST'])
@login_required
def noticeRead(user=None):
    notice_id = request.json["notice_id"]
    noticeStatus = NoticeStatus(user_id = user.uid, notice_id = notice_id)

    db.session.add(noticeStatus)
    return {"result": 0}, status.HTTP_200_OK

@route(app=api_v1, path='/notice/getUnreadCount', methods=['POST'])
@login_required
def getUnreadCount(user=None):
    total = Notice.query.filter(or_(Notice.user_id == user.uid, Notice.user_id == 0)).count()
    read = NoticeStatus.query.filter(NoticeStatus.user_id == user.uid).count()

    return {"result": total - read}, status.HTTP_200_OK