from flask import Blueprint


api_v1 = Blueprint('api_v1', __name__)

from backend.controllers.v1 import users
from backend.controllers.v1 import timetable
from backend.controllers.v1 import community
from backend.controllers.v1 import comment
from backend.controllers.v1 import notice
