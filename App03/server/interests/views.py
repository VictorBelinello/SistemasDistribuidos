import json

from flask import abort, jsonify, request

from ..market import default_market
from . import interests_bp

INTERESTS = {}

def make_response(symbs):
  response = {}
  for symb in symbs:
    response[symb] = default_market.symbols[symb]
  return response

def get_data(request, id=None):
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
  if request.method == "DELETE":
    if data['symbol'] not in INTERESTS[id]:
      abort(404, description=f"Symbol {data['symbol']} not found on interests.")

  return data

@interests_bp.route('', methods=['GET'])
def get(id):
  if id not in INTERESTS:
    INTERESTS[id] = []
  # Atualiza as cotacoes de interesse antes de devolver
  response = {}
  for symb in INTERESTS[id]:
    response[symb] = default_market.symbols[symb]
  return {"status":"GET successful","data": response}

@interests_bp.route('', methods=['POST'])
def post(id):
  if id not in INTERESTS:
    INTERESTS[id] = []

  data = get_data(request)

  data['quote'] = default_market.symbols[data['symbol']]
  # Adiciona symbol na lista de cotacoes do usuario 'id'
  INTERESTS[id].append(data['symbol'])
  return {"status":"POST successful","data":data}

@interests_bp.route('', methods=['DELETE'])
def delete(id):
  if id not in INTERESTS:
    return {"status": "DELETE not done", "data": f"Requested by {id}"}

  data = get_data(request, id)

  INTERESTS[id].remove(data['symbol'])
  return {"status":"DELETE successful","data":data['symbol']}
  
