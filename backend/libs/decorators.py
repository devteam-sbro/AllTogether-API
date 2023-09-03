import json
import logging
from datetime import datetime
from functools import wraps

from flask import request, Response
from flask_api import status

from backend.libs.LoggedThread import LoggedThread
from backend.libs.database import db
from backend.libs.hash import generate_request_id

from backend.models.users import Session


log = logging.getLogger('kook-server')

logging_outsiders = ['get_notices', 'search_orders']


def validate(required, target):
    missing_args = list(set(required) - set(target))
    if len(missing_args) == 0:
        return None
    return missing_args


def with_model(model):
    def _model(func):
        @wraps(func)
        def process(*args, **kwargs):
            required_args = model
            request_param = request.get_json()

            missing_args = validate(required_args, request_param)
            if missing_args is None:
                return func(data=request_param, *args, **kwargs)

            errmsg = {
                'err': 'Missing required arguments',
                'data': {'missing_args': missing_args}
            }
            return errmsg, status.HTTP_400_BAD_REQUEST

        return process

    return _model


def route(app, path, methods):
    def _inner(func):
        @wraps(func)

        @app.route(path, methods=methods, endpoint=func.__name__)
        def app_route(*args, **kwargs):
            api_name = func.__name__
            api_version = app.name
            # temp_log = create_temp_log(func.__name__)

            if api_name == 'download_file':
                return func(*args, **kwargs)

            try:
                response_msg, status_code = func(*args, **kwargs)
            except TypeError as e:
                log.exception(e)
                # fill_temp_log(create_temp_log('exception', commit=False), traceback.format_exc())
                response_msg = "Request body dose not json format"
                status_code = status.HTTP_400_BAD_REQUEST
            except Exception as e:
                log.exception(e)
                # fill_temp_log(create_temp_log('exception', commit=False), traceback.format_exc())
                response_msg = str(e)
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            if type(response_msg) in (dict, list):
                response_msg = json.dumps(response_msg, ensure_ascii=False)

            req_id = generate_request_id()
            response = Response(response_msg, status=status_code,
                                mimetype='application/json; charset=utf-8')
            response.headers['X-Request-ID'] = req_id

            client_ip = request.environ.get('X-Forwarded-For')#.split(',')[0] if current_app.config.get('QA') is True else request.headers.get('X-Forwarded-For').split(',')[0]
            user_agent = request.headers.get('User-Agent')
            session_key = request.headers.get('X-Authorization') or ''
            # session = Session.get_session(session_key)
            # logmsg = {
            #     'request_id': str(req_id),
            #     'api_name': api_name,
            #     'api_version': api_version,
            #     'request_method': request.method,
            #     'request_path': request.path,
            #     'request_header': request.headers,
            #     'request_body': '',
            #     'request_args': '',
            #     'response_code': status_code,
            #     'response_data': response_msg,
            #     'client_ip': client_ip,
            #     'user_idx': session.user.idx if session is not None else '',
            #     'user_agent': user_agent
            # }

            # if request.method == 'GET':
            #     logmsg['request_args'] = request.args.to_dict()
            # else:
            #     logmsg['request_body'] = request.get_json()
            #
            # log_msg = pprint.pformat(logmsg)
            # log.debug(log_msg)
            # log.debug('\n\n\n')
            # fill_temp_log(temp_log, log_msg if api_name not in logging_outsiders else '')
            return response

        return app_route

    return _inner


def login_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        session_key = request.headers.get('X-Authorization')

        if session_key is None:
            msg = {'err': 'Access Denied', 'data': 'Login Required'}
            return msg, status.HTTP_401_UNAUTHORIZED

        session = Session.get_session(session_key)
        if session is None:
            msg = {'err': 'Access Denied', 'data': 'Login Required'}
            return msg, status.HTTP_401_UNAUTHORIZED

        if session.is_expired():
            msg = {'err': 'Session expired', 'data': 'Session expired'}
            return msg, status.HTTP_401_UNAUTHORIZED
        session.user.session_key = session.session_key
        session.user.last_access = datetime.now()
        db.session.flush()
        ret = func(user=session.user, *args, **kwargs)
        db.session.commit()
        return ret

    return decorated


def run_async(func):
    """
        run_async(func)
            function decorator, intended to make "func" run in a separate
            thread (asynchronously).
            Returns the created Thread object

            E.g.:
            @run_async
            def task1():
                do_something

            @run_async
            def task2():
                do_something_too

            t1 = task1()
            t2 = task2()
            ...
            t1.join()
            t2.join()
    """
    @wraps(func)
    def async_func(*args, **kwargs):
        thread = LoggedThread(target=func, args=args, kwargs=kwargs, wait=kwargs.get('wait', 0))
        thread.start()
        return thread

    return async_func


