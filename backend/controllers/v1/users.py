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
from backend.models.school import School
from backend.models.community import Community
from backend.models.community_photo import CommunityPhoto
from backend.models.community_like import CommunityLike
from backend.models.community_scrap import CommunityScrap
from backend.models.community_report import CommunityReport

log = logging.getLogger('kook-server')


@route(app=api_v1, path='/users/signup', methods=['POST'])
@with_model(model=User.add_user)
def add_user(data):
    email = data['email']

    # if data.get('with_sms'):
    #     if not SmsAuth.validate_sms_auth(data.get('auth_key'),
    #                                      data.get('auth_value')):
    #         return {'err': 'Invalid sms auth'}, status.HTTP_400_BAD_REQUEST

    try:
        gen_pwd = generate_password_hash(data['pwd'])
        user = User(school_id=data['school_id'], email=email, pwd=gen_pwd,
                    nickname=data['nickname'], name=data['name'], phone=data['phone'], dev_type=data['dev_type'], dev_token=data['dev_token'],
                    add_time=datetime.now(timezone('Asia/Seoul')))
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        # Duplicated on Email
        db.session.rollback()
        response_msg = {'err': 'Email already existed', 'data': email}
        status_code = status.HTTP_409_CONFLICT
        return response_msg, status_code

    newUser = User.query.filter_by(email=email).first()

    resSchool = db.session.query(School).filter(School.uid == newUser.school_id).first()
    if(resSchool is not None and resSchool.json["name"] is not None):
        newUser.school_name = resSchool.json["name"]

    session_stuff = '%s/%s/%s' % (newUser.email, newUser.pwd, time.time())
    session_key = generate_password_hash(session_stuff)
    Session.set_session(session_key, newUser)

    newUser.dev_type = data['dev_type']
    newUser.dev_token = data['dev_token']
    newUser.access_token = session_key.decode('utf-8')
    return {'result': 0, 'data': newUser.json}, status.HTTP_200_OK

@route(app=api_v1, path='/users/login', methods=['POST'])
@with_model(model=User.login)
def login(data):
    email = data['email']
    pwd = data['pwd']

    user = User.query.filter_by(email=email).first()
    if not user:
        msg = {'result': -1, 'msg': 'User not found'}
        return msg, status.HTTP_200_OK

    if not check_password_hash(user.pwd, pwd):
        msg = {'result': -2, 'msg': 'Wrong password'}
        return msg, status.HTTP_200_OK

    session_stuff = '%s/%s/%s' % (user.email, user.pwd, time.time())
    session_key = generate_password_hash(session_stuff)
    Session.set_session(session_key, user)

    user.dev_type = data['dev_type']
    user.dev_token = data['dev_token']
    user.access_token = session_key.decode('utf-8')
    resSchool = db.session.query(School).filter(School.uid == user.school_id).first()

    if(resSchool is not None and resSchool.json["name"] is not None):
        user.school_name = resSchool.json["name"]

    msg = {'result': 0, 'data': user.json}

    db.session.commit()
    return msg, status.HTTP_200_OK

@route(app=api_v1, path='/app_info', methods=['POST'])
def app_info():
    r_data = {'version': '1.0', 'email': 'alltogether@app.com'}
    return {'result': 0, 'data': r_data}, status.HTTP_200_OK

@route(app=api_v1, path='/users/update', methods=['POST'])
@login_required
def update_user(user):
    data = request.json
    changed = False
    for k, v in data.items():
        if k not in User.updatable_column:
            log.error("[Update User] Invalid Column : %s" % k)
            errmsg = {
                'err': 'Invalid update key',
                'data': '%s is invalid updatable key' % k
            }
            return errmsg, status.HTTP_400_BAD_REQUEST
        changed = True
        if k == "pwd":
            v = generate_password_hash(v)
        user.update_column(k, v)
    if changed:
        db.session.commit()
    return {'result': 0}, status.HTTP_200_OK

@route(app=api_v1, path='/users/password_reset', methods=['POST'])
def password_reset():
    data = request.json
    email = data['email']
    pwd = data['pwd']

    v = generate_password_hash(pwd)
    user = User.query.filter_by(email=email).first()
    if not user:
        errmsg = {'result': -1, 'msg': 'User not found'}
        return errmsg, status.HTTP_404_NOT_FOUND
    user.update_column("pwd", v)
    db.session.commit()
    return {'result': 0}, status.HTTP_200_OK


@route(app=api_v1, path='/users/logout', methods=['POST'])
@login_required
def logout(user):
    session = Session.query.get(user.session_key)
    session.activated = 0
    user.update_column("dev_token", '')
    db.session.commit()
    return {'result': 0}, status.HTTP_200_OK

@route(app=api_v1, path='/users/withdrawal', methods=['POST'])
@login_required
def withdrawal(user):
    session = Session.query.get(user.session_key)
    session.activated = 0
    user.update_column("del_time", datetime.now(timezone('Asia/Seoul')))
    db.session.commit()
    return {'result': 0}, status.HTTP_200_OK

@route(app=api_v1, path='/users/check_nickname', methods=['POST'])
def check_nickname():
    data = request.json
    user = User.query.filter_by(nickname=data["nickname"]).first()
    if not user:
        return {'result': 0}, status.HTTP_200_OK
    msg = {'result': -1, 'msg': 'Nickname already exists', 'data':{}}
    return msg, status.HTTP_200_OK

@route(app=api_v1, path='/users/phone_auth', methods=['POST'])
def phone_auth():
    data = request.json
    user = User.query.filter_by(phone=data["phone"]).first()
    if not user:
        msg = {'result': 0, 'data': {"auth_num": "123"}}  # ToDO YJ return auth_num
        return msg, status.HTTP_200_OK
    msg = {'result': -1, 'msg': 'Phone Not Found'}
    return msg, status.HTTP_200_OK

@route(app=api_v1, path='/users/email_auth', methods=['POST'])
def email_auth():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if not user:
        msg = {'result': -1, 'msg': 'Email Not Found', 'data': {"auth_num":"123"}}
        return msg, status.HTTP_200_OK
    msg = {'result': 0, 'data': {"auth_num":"123"}} #ToDO YJ return auth_num
    return msg, status.HTTP_200_OK

@route(app=api_v1, path='/users/school_search', methods=['POST'])
def school_search():
    data = request.json

    result = db.session.query(School).filter((School.name.contains(data["keyword"]))).all()
    data = [r.json for r in result]
    return {'result': 0, 'data': {'list': data}}, status.HTTP_200_OK

@route(app=api_v1, path='/users/get_my_post', methods=['POST'])
@login_required
def GetMyPost(user):
    data = request.json

    pageNumber = data["page"]
    limit = 10

    totalCnt = len(db.session.query(Community).filter(Community.user_id == user.uid).all())

    result = db.session.query(Community).filter(Community.user_id == user.uid)\
        .limit(limit).offset(limit * pageNumber)\
        .all()

    ret = []
    for r in result:
        if(r.add_time is not None):
            r.add_time = r.add_time.strftime('%Y-%m-%d %H:%M:%S')
        like = db.session.query(CommunityLike).filter((CommunityLike.community_id == r.uid)).all()
        photo = db.session.query(CommunityPhoto).filter((CommunityPhoto.community_id == r.uid)).all()
        scrap = db.session.query(CommunityScrap).filter((CommunityScrap.community_id == r.uid)).all()
        j = r.json
        j["like_cnt"] = len(like)
        j["photo"] = len(photo)
        j["scrap"] = len(scrap)
        user = db.session.query(User).filter(User.uid == r.user_id).first()
        if(user is not None):
            school = db.session.query(School).filter(School.uid == user.school_id).first()
            if(school is not None):
                j["school_id"] = school.uid
                j["school_name"] = school.name
        ret.append(j)

    isLast = pageNumber >= -(-totalCnt // limit) - 1

    return {"result": 0, "data": {"total_count": totalCnt,
            "is_last": isLast,
            "list": ret
            }}, status.HTTP_200_OK

@route(app=api_v1, path='/users/get_my_comment', methods=['POST'])
@login_required
def GetMyComment(user):
    data = request.json

    pageNumber = data["page"]
    limit = 10

    sql = "select t_community.* from t_community left join t_comment on t_comment.community_id = t_community.uid " \
          "where t_comment.user_id = :user_uid  group by t_community.user_id"
    resultTotal = Community.query.from_statement(text(sql)) \
        .params(user_uid=user.uid).all()

    totalCnt = len(resultTotal)

    sql1 = "select t_community.* from t_community left join t_comment on t_comment.community_id = t_community.uid " \
          "where t_comment.user_id = :user_uid  group by t_community.user_id limit :limit offset :offset"
    result = Community.query.from_statement(text(sql1)) \
        .params(user_uid=user.uid, limit=limit, offset=limit * pageNumber).all()


    ret = []
    for r in result:
        like = CommunityLike.query.filter((CommunityLike.community_id == r.uid)).all()
        photo = CommunityPhoto.query.filter((CommunityPhoto.community_id == r.uid)).all()
        scrap =CommunityScrap.query.filter((CommunityScrap.community_id == r.uid)).all()
        j = r.json
        j["like_cnt"] = len(like)
        j["photo"] = len(photo)
        j["scrap"] = len(scrap)
        user = User.query.filter(User.uid == r.user_id).first()
        if (user is not None):
            school = School.query.filter(School.uid == user.school_id).first()
            if (school is not None):
                j["school_id"] = school.uid
                j["school_name"] = school.name
        ret.append(j)

    isLast = pageNumber >= -(-totalCnt // limit) - 1

    return {"result": 0, "data": {"total_count": totalCnt,
            "is_last": isLast,
            "list": ret
            }}, status.HTTP_200_OK

@route(app=api_v1, path='/users/get_my_scrap', methods=['POST'])
@login_required
def GetMyScrap(user):
    data = request.json

    pageNumber = data["page"]
    limit = 10

    sql = "select t_community.* from t_community_scrap left join t_community on t_community_scrap.community_id = t_community.uid " \
          "where t_community_scrap.user_id = :user_uid"
    resultTotal = Community.query.from_statement(text(sql)) \
        .params(user_uid=user.uid).all()

    totalCnt = len(resultTotal)
    sql1 = "select t_community.* from t_community_scrap left join t_community on t_community_scrap.community_id = t_community.uid " \
          "where t_community_scrap.user_id = :user_uid limit :limit offset :offset"
    result = Community.query.from_statement(text(sql1)) \
        .params(user_uid=user.uid, limit=limit, offset=limit * pageNumber).all()

    ret = []
    for r in result:
        if r is None:
            break
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

    isLast = pageNumber >= -(-totalCnt // limit) - 1

    return {"result": 0, "data": {"total_count": totalCnt,
                                  "is_last": isLast,
                                  "list": ret
                                  }}, status.HTTP_200_OK