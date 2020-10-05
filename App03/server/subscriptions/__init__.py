from flask import Blueprint

subscriptions_bp = Blueprint("subscriptions", __name__, url_prefix='/subscriptions/<string:id>')

from . import views
