from flask import abort, request

from ..market import default_market
from . import interests_bp

INTERESTS = {}

from server.common import get_data

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

  data = get_data(request)

  if data['symbol'] not in INTERESTS[id]:
      abort(404, description=f"Symbol {data['symbol']} not found on interests.")

  INTERESTS[id].remove(data['symbol'])
  return {"status":"DELETE successful","data":data['symbol']}
  
