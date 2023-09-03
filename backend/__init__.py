from logging.config import dictConfig

from flask import Flask

app = Flask(__name__)

app.config.from_pyfile('config.cfg', silent=True)


def _startup():
    # dictConfig(app.config['LOGGING'])

    from backend.controllers.v1 import api_v1
    from backend.controllers.common import version, banner, ad
    app.register_blueprint(api_v1, url_prefix='/v1')


_startup()
