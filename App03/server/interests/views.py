from flask import abort, request

from ..market import default_market
from . import interests_bp

INTERESTS = {}

from server.common import get_data, make_response

@interests_bp.route('', methods=['GET'])
def get(id):
  if id not in INTERESTS:
    INTERESTS[id] = []
  # Atualiza as cotacoes de interesse antes de devolver
  response = {}
  for symb in INTERESTS[id]:
    response[symb] = default_market.symbols[symb]
  return make_response(200, response)

@interests_bp.route('', methods=['POST'])
def post(id):
  if id not in INTERESTS:
    INTERESTS[id] = []

  status, data = get_data(request)
  if status != 200:
    return make_response(status, data)
    
  data['quote'] = default_market.symbols[data['symbol']]
  # Adiciona symbol na lista de cotacoes do usuario 'id'
  INTERESTS[id].append(data['symbol'])
  return  make_response(200, '')

@interests_bp.route('', methods=['DELETE'])
def delete(id):
  if id not in INTERESTS:
    return make_response(404,"You have no interests registered yet.")

  status, data = get_data(request)
  if status != 200:
    return make_response(status, data)

  if data['symbol'] not in INTERESTS[id]:
      return make_response(404, f"Symbol {data['symbol']} not found on interests.") 

  INTERESTS[id].remove(data['symbol'])
  return make_response(status, data['symbol'])
  
