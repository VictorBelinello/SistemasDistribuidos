import random

from . import transactions_bp
from flask import request
from server.common import get_data, make_response

from ..market import default_market

TRANSACTIONS = {
  'buy': [],
  'sell': []
}

STOCKS = {}

def get_random_stocks():
  symbols = default_market.get_random_symbols()
  stocks = {}
  for s in symbols:
    stocks[s] = random.randint(1, 5)
  return stocks

@transactions_bp.route('', methods=['GET'])
def get_stocks(id):
  if id not in STOCKS:
    # Primeira vez, da algumas acoes iniciais
    STOCKS[id] = get_random_stocks()
  return make_response(200, STOCKS[id])

@transactions_bp.route('/buy', methods=['POST'])
def post_buy(id):
  status, data = get_data(request)
  if status != 200:
    return make_response(status, data) 
  TRANSACTIONS['buy'].append(data)
  return make_response(status, '') 

@transactions_bp.route('/sell', methods=['POST'])
def post_sell(id):
  status, data = get_data(request)
  if status != 200:
    return make_response(status, data) 
  TRANSACTIONS['sell'].append(data)
  return make_response(status, '') 