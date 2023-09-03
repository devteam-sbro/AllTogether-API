import json


def json_to_dict(payload):
    return json.loads(payload.decode('utf8'))


def get_default_header(auth=None):
    result = {
        'X-Forwarded-for': '123,123'
    }
    if auth:
        result['X-Authorization'] = auth
    return result
