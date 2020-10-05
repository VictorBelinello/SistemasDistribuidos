from . import default_market, market_bp


@market_bp.route('/')
def get_all():
  return {"status":"GET successful","data": default_market.symbols}
