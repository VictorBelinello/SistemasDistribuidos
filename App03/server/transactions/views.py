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

def can_trade(sell, buy):
  return ( 
  sell['owner'] != buy['owner'] and 
  sell['symbol'] == buy['symbol'] and
  sell['amount'] == buy['amount'] and
  sell['price'] == buy['price'] )

def check_transactions():
  selling = TRANSACTIONS['sell']
  buying = TRANSACTIONS['buy']
  for sell in selling:
    for buy in buying:
      if can_trade(sell, buy):
        print("Vendendo ", sell)
        print("Comprando ", buy)

def can_sell(id, transaction):
  symbol = transaction['symbol']
  amount = int(transaction['amount'])
  return symbol in STOCKS[id] and amount == STOCKS[id][symbol]

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
  check_transactions()
  return make_response(status, '') 

@transactions_bp.route('/sell', methods=['POST'])
def post_sell(id):
  status, data = get_data(request)
  if status != 200:
    return make_response(status, data) 
  if not can_sell(id, data):
    return make_response(500, "You don't have enough stocks for this transaction.")
  TRANSACTIONS['sell'].append(data)
  check_transactions()
  return make_response(status, '') 