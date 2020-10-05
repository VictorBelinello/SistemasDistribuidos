from flask import Blueprint

interests_bp = Blueprint("interests", __name__, url_prefix='/interests/<string:id>')

from . import views
