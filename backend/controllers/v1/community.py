import json
import logging
import random
import time

from datetime import datetime
from pytz import timezone

from flask import request
from flask_api import status
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text

from backend import app
from backend.controllers.v1 import api_v1
from backend.libs.database import db
from backend.libs.decorators import login_required, with_model, route
from backend.libs.hash import generate_password_hash, check_password_hash
from backend.libs.validator import check_optional_args
from backend.models.users import User, Session
from backend.models.community import Community
from backend.models.community_photo import CommunityPhoto
from backend.models.community_like import CommunityLike
from backend.models.community_scrap import CommunityScrap
from backend.models.community_report import CommunityReport
from backend.models.comment import Comment, CommentLike, CommentScrap
from backend.models.school import School
from sqlalchemy import and_, or_

log = logging.getLogger('kook-server')


@route(app=api_v1, path='/community', methods=['POST'])
@login_required
def add_community(user=None, data=None):
    data = request.json["content"]
    community = Community(user_id=user.uid, title=data["title"], content=data["content"],
                          anonym=data["anonym"], add_time=datetime.now(timezone('Asia/Seoul')))
    db.session.add(community)
    db.session.commit()

    photos = data["photos"]
    for p in photos:
        community_photo = CommunityPhoto(community_id=community.uid, img=p["url"], img_title=p["title"])
        db.session.add(community_photo)
    db.session.commit()
    return {'result': 0}, status.HTTP_200_OK


@route(app=api_v1, path='/community/like', methods=['POST'])
@login_required
def community_like(user):
    data = request.json
    communityLike = CommunityLike(user_id=user.uid, community_id=data["community_id"],
                                  add_time=datetime.now(timezone('Asia/Seoul')))

    isLike = db.session.query(CommunityLike).filter(
        (CommunityLike.community_id == data["community_id"]) and (CommunityLike.user_id == user.uid)).first()
    if isLike is None:
        db.session.add(communityLike)
        db.session.commit()
        return {'result': 0}, status.HTTP_200_OK
    else:
        return {'result': -1}, status.HTTP_200_OK

@route(app=api_v1, path='/community/scrap', methods=['POST'])
@login_required
def community_scrap(user):
    data = request.json
    communityScrap = CommunityScrap(user_id=user.uid, community_id=data["community_id"],
                                    add_time=datetime.now(timezone('Asia/Seoul')))

    isScrap = db.session.query(CommunityScrap).filter(
        (and_(CommunityScrap.community_id == data["community_id"], CommunityScrap.user_id == user.uid))).first()
    if isScrap is None:
        db.session.add(communityScrap)
        db.session.commit()
        return {'result': 0}, status.HTTP_200_OK
    else:
        db.session.delete(isScrap)
        db.session.commit()
        return {'result': 0}, status.HTTP_200_OK



@route(app=api_v1, path='/community/report', methods=['POST'])
@login_required
def community_report(user=None):
    data = request.json
    communityReport = CommunityReport(user_id=user.uid, community_id=data["community_id"],
                                      reason=data["reason"],
                                      add_time=datetime.now(timezone('Asia/Seoul')))

    isReport = db.session.query(CommunityReport).filter(
        (CommunityReport.community_id == data["community_id"]) and
        (CommunityReport.user_id == user.uid) and
        (CommunityReport.reason == data["reason"])).first()
    if isReport is None:
        db.session.add(communityReport)
        db.session.commit()
        return {'result': 0}, status.HTTP_200_OK

    return {'result': 1}, status.HTTP_409_CONFLICT


@route(app=api_v1, path='/community/search', methods=['POST'])
def community_search():
    data = request.json
    page = data["page"]
    limit = 10

    totalCnt = Community.query.filter(
        or_(Community.title.contains(data["keyword"]), Community.content.contains(data["keyword"]))).count()

    result = db.session.query(Community).filter(
        or_(Community.title.contains(data["keyword"]), Community.content.contains(data["keyword"]))).limit(10).offset(
        page * limit).all()

    ret = []
    for r in result:
        r.add_time = r.add_time.strftime('%Y-%m-%d %H:%M:%S')
        like = db.session.query(CommunityLike).filter((CommunityLike.community_id == r.uid)).all()
        photo = db.session.query(CommunityPhoto).filter((CommunityPhoto.community_id == r.uid)).all()
        scrap = db.session.query(CommunityScrap).filter((CommunityScrap.community_id == r.uid)).all()
        j = r.json
        j["like_cnt"] = len(like)
        j["photo"] = len(photo)
        j["scrap"] = len(scrap)
        user = db.session.query(User).filter(User.uid == r.user_id).first()
        if (user is not None):
            school = db.session.query(School).filter(School.uid == user.school_id).first()
            if (school is not None):
                j["school_id"] = school.uid
                j["school_name"] = school.name
        ret.append(j)

    isLast = page >= -(-totalCnt // limit) - 1

    return {"result": 0, "data": {"total_count": totalCnt,
                                  "is_last": isLast,
                                  "list": ret
                                  }}, status.HTTP_200_OK


@route(app=api_v1, path='/community/all', methods=['POST'])
def community_all():
    data = request.json
    sId = data["school_id"]
    page = data["page"]
    limit = 10

    totalCnt = Community.query.filter(
        and_(User.school_id == sId, User.uid == Community.user_id)).count() if sId > 0 else \
        Community.query.count()

    result = db.session.query(Community).filter(and_(User.school_id == sId, User.uid == Community.user_id)).limit(
        10).offset(page * limit).all() if sId > 0 \
        else db.session.query(Community).limit(10).offset(page * limit).all()

    ret = []
    for r in result:
        r.add_time = r.add_time.strftime('%Y-%m-%d %H:%M:%S')
        like = db.session.query(CommunityLike).filter((CommunityLike.community_id == r.uid)).all()
        photo = db.session.query(CommunityPhoto).filter((CommunityPhoto.community_id == r.uid)).all()
        scrap = db.session.query(CommunityScrap).filter((CommunityScrap.community_id == r.uid)).all()
        j = r.json
        j["like_cnt"] = len(like)
        j["photo"] = len(photo)
        j["scrap"] = len(scrap)
        user = db.session.query(User).filter(User.uid == r.user_id).first()
        if (user is not None):
            school = db.session.query(School).filter(School.uid == user.school_id).first()
            if (school is not None):
                j["school_id"] = school.uid
                j["school_name"] = school.name
        ret.append(j)

    isLast = page >= -(-totalCnt // limit) - 1

    return {"result": 0, "data": {"total_count": totalCnt,
                                  "is_last": isLast,
                                  "list": ret
                                  }}, status.HTTP_200_OK


@route(app=api_v1, path='/community/popular', methods=['POST'])
def community_popular():
    school_id = request.json["school_id"]

    if (school_id > 0):
        sql = "SELECT C.*,U.school_id," \
              "(SELECT count(*)*2 FROM t_comment M WHERE M.community_id = C.uid) AS comment_cnt," \
              "(SELECT count(*) FROM t_community_like L WHERE L.community_id = C.uid) AS like_cnt " \
              "FROM `t_community` C LEFT JOIN t_user U on U.uid = C.user_id " \
              "WHERE DATE_FORMAT(subdate(now(),1),'%Y/%m/%d') = DATE_FORMAT(C.add_time,'%Y/%m/%d') AND school_id = :school_id " \
              "GROUP BY C.uid " \
              "ORDER BY comment_cnt+like_cnt DESC " \
              "LIMIT 2"
    else:
        sql = "SELECT C.*,U.school_id," \
              "(SELECT count(*)*2 FROM t_comment M WHERE M.community_id = C.uid) AS comment_cnt," \
              "(SELECT count(*) FROM t_community_like L WHERE L.community_id = C.uid) AS like_cnt " \
              "FROM `t_community` C LEFT JOIN t_user U on U.uid = C.user_id " \
              "WHERE DATE_FORMAT(subdate(now(),1),'%Y/%m/%d') = DATE_FORMAT(C.add_time,'%Y/%m/%d') " \
              "GROUP BY C.uid " \
              "ORDER BY comment_cnt+like_cnt DESC " \
              "LIMIT 2"
    result = db.session.query(Community).from_statement(text(sql)) \
        .params(school_id=school_id).all()

    ret = []
    for r in result:
        if (r.add_time is not None):
            r.add_time = r.add_time.strftime('%Y-%m-%d %H:%M:%S')
        like = db.session.query(CommunityLike).filter((CommunityLike.community_id == r.uid)).all()
        photo = db.session.query(CommunityPhoto).filter((CommunityPhoto.community_id == r.uid)).all()
        scrap = db.session.query(CommunityScrap).filter((CommunityScrap.community_id == r.uid)).all()
        j = r.json
        j["like_cnt"] = len(like)
        j["photo"] = len(photo)
        j["scrap"] = len(scrap)
        user = db.session.query(User).filter(User.uid == r.user_id).first()
        if (user is not None):
            school = db.session.query(School).filter(School.uid == user.school_id).first()
            if (school is not None):
                j["school_id"] = school.uid
                j["school_name"] = school.name
        ret.append(j)
    ret = {"result": 0, "data": {"list": ret}}
    return ret, status.HTTP_200_OK


@route(app=api_v1, path='/community/detail', methods=['POST'])
@login_required
def community_detail(user):
    data = request.json
    cId = data["community_id"]
    page = data["page"]
    limit = 10

    sql = "SELECT *, case when parent=0 then uid else parent end commentGroup" \
          " FROM `t_comment`" \
          " where community_id = :community_id" \
          " ORDER BY commentGroup DESC, add_time DESC" \
          " LIMIT 10" \
          " OFFSET :page"
    res = db.session.query(Comment).from_statement(text(sql)) \
        .params(community_id=cId, page=page * limit).all()

    sql1 = "SELECT *, case when parent=0 then uid else parent end commentGroup" \
           " FROM `t_comment`" \
           " where community_id = :community_id" \
           " ORDER BY commentGroup DESC, add_time DESC"
    totalCnt = len(db.session.query(Comment).from_statement(text(sql1)) \
                   .params(community_id=cId, page=page * limit).all())

    result = db.session.query(Community).filter(Community.uid == cId).first()
    ret = result.json
    commentRet = [a.json for a in res]
    for a in commentRet:
        likeCommentRet = db.session.query(CommentLike).filter(
            and_(CommentLike.user_id == user.uid, CommentLike.comment_id
                 == a["uid"])).first()
        likeCommentState = 1
        if likeCommentRet is None:
            likeCommentState = 0
        a['isLike'] = likeCommentState

    for a in commentRet:
        scrapCommentRet = db.session.query(CommentScrap).filter(
            and_(CommentScrap.user_id == user.uid, CommentScrap.comment_id
                 == a["uid"])).first()
        scrapCommentState = 1
        if scrapCommentRet is None:
            scrapCommentState = 0
        a['isScrap'] = scrapCommentState

    ret["comments"] = json.loads(json.dumps(commentRet))

    likeRet = db.session.query(CommunityLike).filter(and_(CommunityLike.user_id == user.uid, CommunityLike.community_id
                                                     == cId)).first()
    likeState = 1
    if likeRet is None:
        likeState = 0

    ret['isLike'] = likeState

    scrapRet = db.session.query(CommunityScrap).filter(and_(CommunityScrap.user_id == user.uid, CommunityScrap.community_id
                                                          == cId)).first()
    scrapState = 1
    if scrapRet is None:
        scrapState = 0

    ret['isScrap'] = scrapState

    like = db.session.query(CommunityLike).filter((CommunityLike.community_id == result.uid)).all()
    photo = db.session.query(CommunityPhoto).filter((CommunityPhoto.community_id == result.uid)).all()
    scrap = db.session.query(CommunityScrap).filter((CommunityScrap.community_id == result.uid)).all()
    j = ret
    j["like_cnt"] = len(like)
    j["photo"] = len(photo)
    j["scrap"] = len(scrap)
    user = db.session.query(User).filter(User.uid == result.user_id).first()
    if (user is not None):
        school = db.session.query(School).filter(School.uid == user.school_id).first()
        if (school is not None):
            j["school_id"] = school.uid
            j["school_name"] = school.name

    isLast = page >= -(-totalCnt // limit) - 1
    j["total_count"] = totalCnt
    j["isLast"] = isLast

    return {"result": 0, "data": j}, status.HTTP_200_OK
