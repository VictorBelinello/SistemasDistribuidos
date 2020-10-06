from . import default_market, market_bp

from server.common import make_response

@market_bp.route('/')
def get_all():
  return make_response(200, default_market.symbols)
