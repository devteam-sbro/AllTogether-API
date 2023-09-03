import binascii
import hashlib
import string
import uuid
import random
import time

from werkzeug.security import safe_str_cmp

from backend import app


def generate_password_hash(data):
    salt = app.config['PASSWORD_SALT'].encode('utf-8')
    dk = hashlib.pbkdf2_hmac('sha256', data.encode('utf-8'), salt, 100000)
    return binascii.hexlify(dk)


def check_password_hash(pwhash, passwd):
    hashval = generate_password_hash(passwd)
    return safe_str_cmp(pwhash, hashval)


def generate_request_id():
    return uuid.uuid4()

def generate_unique_name():
    RANDOMSTR = "0123456789abcdef"
    unique_name = format(int(time.time()), "x")
    for _ in range(3):
        unique_name += RANDOMSTR[random.randint(0, len(RANDOMSTR) - 1)]
    return unique_name
