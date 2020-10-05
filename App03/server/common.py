import json
from flask import abort

from .market import default_market

def get_data(request):
  # Pega json do request
  if not request.is_json:
    data = json.loads(request.get_data())
  else:
    data = request.get_json()

  # Trata possiveis erros
  if not data:
    abort(404, description=f"{request.method} failed to get data. Request data:\n{request.get_data()}")
  if 'symbol' not in data:
    abort(404, description=f"Key 'symbol' not found on JSON sent on {request.method} request. Only got:\n{data}")
  if data['symbol'] not in default_market.symbols:
    abort(404, description=f"Symbol {data['symbol']} not found on available market.")

  return data