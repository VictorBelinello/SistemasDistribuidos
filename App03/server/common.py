import json
from flask import abort

from .market import default_market

def get_data(request):
  status = 200

  if not request.is_json:
    abort(500, description=f"This server only receives JSON. {request.method} Request:\n{request.headers}")
  else:
    # Pega json do request
    data = request.get_json()

  # Trata possiveis erros
  if not data:
    status = 404
    data = f"{request.method} failed to get data. Request data:\n{request.get_data()}"
  if 'symbol' not in data:
    status = 404
    data = f"Key 'symbol' not found on JSON sent on {request.method} request. Only got:\n{data}"
  if data['symbol'] not in default_market.symbols:
    status = 404
    data = f"Symbol {data['symbol']} not found on available market."

  return status, data

def make_response(status, data):
  return {"status": status, "data": data}