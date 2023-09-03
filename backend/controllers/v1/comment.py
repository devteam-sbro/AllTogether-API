
from datetime import datetime
from pytz import timezone

from flask import request
from flask_api import status
from backend.controllers.v1 import api_v1
from backend.libs.database import db
from backend.libs.decorators import login_required, with_model, route
from backend.models.comment import Comment, CommentLike, CommentScrap
from backend.models.community import Community
from backend.models.notice import Notice
from backend.models.users import User
from backend.models.school import School
from sqlalchemy import and_, or_



@route(app=api_v1, path='/comment', methods=['POST'])
@with_model(model=Comment.add_comment)
@login_required
def add_comment(data=None, user=None):
    # data = request.json
    comment = Comment(community_id=data["community_id"], user_id=user.uid, content=data["content"],
                          anonym=data["anonym"], parent=data["parent"], add_time=datetime.now(timezone('Asia/Seoul')))
    db.session.add(comment)
    db.session.commit()

    title = "Your post has been commented on."
    if data["parent"] != '0':
        title = "Your comment has been commented on."

    community = Community.query.filter(Community.uid == data["community_id"]).first()
    if community is not None:
        notice = Notice(type=0, user_id=community.user_id, title=title,
                        content=data["content"], community_id=data["community_id"], add_time=datetime.now(timezone('Asia/Seoul')))
        db.session.add(notice)
        db.session.commit()

    ret = comment.json

    return ret, status.HTTP_200_OK

@route(app=api_v1, path='/comment/like', methods=['POST'])
@login_required
def add_comment_like(user=None):
    data = request.json

    commentLike = CommentLike(comment_id=data["comment_id"], user_id=user.uid,
                          add_time=datetime.now(timezone('Asia/Seoul')))
    isLike = db.session.query(CommentLike).filter(
        (CommentLike.comment_id == data["comment_id"]) and (CommentLike.user_id == user.uid)).first()
    if isLike is None:
        db.session.add(commentLike)
        db.session.commit()
        return {'result': 0}, status.HTTP_200_OK
    else:
        return {'result': -1}, status.HTTP_200_OK

@route(app=api_v1, path='/comment/scrap', methods=['POST'])
@login_required
def add_comment_scrap(user=None):
    data = request.json

    commentScrap = CommentScrap(comment_id=data["comment_id"], user_id=user.uid,
                          add_time=datetime.now(timezone('Asia/Seoul')))

    isScrap = db.session.query(CommentScrap).filter(
        (and_(commentScrap.comment_id == data["comment_id"], commentScrap.user_id == user.uid))).first()
    if isScrap is None:
        db.session.add(commentScrap)
        db.session.commit()
        return {'result': 0}, status.HTTP_200_OK
    else:
        db.session.delete(isScrap)
        db.session.commit()
        return {'result': 0}, status.HTTP_200_OK
