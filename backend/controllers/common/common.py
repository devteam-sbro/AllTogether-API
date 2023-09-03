import os
import traceback

import boto3
from flask import request
from flask_api import status

from backend import app
from backend.libs.decorators import route
from backend.libs.ftp_util import FtpUtil
from backend.libs.hash import generate_unique_name

@route(app=app, path='/common/s3/upload', methods=['POST'])
def s3_upload():
    s3_tag = request.form.get("s3_tag")
    image_file = request.files.get("image")

    print(s3_tag)
    print(image_file)

    if s3_tag and image_file:
        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
            )
            new_file_name = generate_unique_name() + \
                            os.path.splitext(image_file.filename)[1]
            s3_client.upload_fileobj(
                image_file,
                app.config['AWS_S3_BUCKET'],
                os.path.join(s3_tag + "/" + new_file_name),
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": image_file.content_type
                }
            )

            image_url = "https://s3.ap-northeast-2.amazonaws.com/{0}/{1}/{2}".format(
                app.config['AWS_S3_BUCKET'], s3_tag, new_file_name)
            return {"result": True, 'image_url': image_url, 'image_name': new_file_name}, status.HTTP_200_OK
        except Exception as e:
            traceback.print_exc()
            return {"result": False,
                    "err": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        return {"result": False,
                "err": "Required field missing"}, status.HTTP_400_BAD_REQUEST

@route(app=app, path='/common/server/upload', methods=['POST'])
def server_upload():
    # s3_tag = request.form.get("s3_tag")
    s3_tag = "community"
    image_file = request.files.get("upload_file")

    if s3_tag and image_file:
        try:
            file_info = FtpUtil.upload_single_file(image_file, s3_tag)
            return {"result": 0, 'data':{'file_url': file_info['file_url'], 'thumb_url': file_info['filename']}}, status.HTTP_200_OK
        except Exception as e:
            traceback.print_exc()
            return {"result": -1,
                    "err": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        return {"result": -1,
                "err": "Required field missing"}, status.HTTP_400_BAD_REQUEST

@route(app=app, path='/uploads/<path:filename>', methods=['GET'])
def download_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
