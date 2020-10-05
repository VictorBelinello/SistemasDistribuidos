from . import transactions_bp
from flask import request
from server.common import get_data

TRANSACTIONS = {
  'buy': [],
  'sell': []
}

@transactions_bp.route('/buy', methods=['POST'])
def post_buy(id):
  transaction = get_data(request)
  print(transaction)
  TRANSACTIONS['buy'].append(transaction)
  return "Buy"

@transactions_bp.route('/sell', methods=['POST'])
def post_sell(id):
  transaction = get_data(request)
  print(transaction)
  TRANSACTIONS['sell'].append(transaction)
  return "Sell"