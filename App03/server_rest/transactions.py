from flask_restful import Resource
from flask import request

from server_rest.util.requests import verify, abort_if, ERRORS, format_sse
from server_rest.util.stocks import get_random_stocks, can_trade

class TransactionsView(Resource):
  def __init__(self, symbols, transactions):
    self.available_symbols = symbols
    self.transactions = transactions

  def get_response(self, id):
    response = self.transactions.clients_stocks[id]
    # Se o GET foi para /buy pega as transacoes de compra do cliente
    if request.path == f'/transactions/{id}/buy':
      response = self.transactions.get_transactions('buy', id)
    # Se o GET foi para /sell pega as transacoes de venda do cliente
    elif request.path == f'/transactions/{id}/sell':
      response = self.transactions.get_transactions('sell', id)
    return response

  def get(self, id):
    if id not in self.transactions.clients_stocks:
      self.transactions.clients_stocks[id] = get_random_stocks(self.available_symbols)
    response = self.get_response(id)

    return {'data': response}

  def put(self, id):
    transaction = verify(request, self.available_symbols)
    transaction['timeout'] = int(transaction['timeout'])
    if request.path == f'/transactions/{id}/buy':
      self.transactions.transactions['buy'].append(transaction)
    elif request.path == f'/transactions/{id}/sell':
      symb = transaction['symbol']
      amount = int(transaction['amount'])
      if symb in self.transactions.clients_stocks[id]:
        if amount <= self.transactions.clients_stocks[id][symb]:
          self.transactions.transactions['sell'].append(transaction)
        else:
          abort_if(ERRORS.RESOURCE_NOT_FOUND, f"You don't have enough stocks of {symb}")
      else:
          abort_if(ERRORS.RESOURCE_NOT_FOUND, f"You don't have stocks of {symb}")

    # Quando uma nova transacao eh inserida verifica se eh possivel vender/comprar algo
    self.transactions.check_transactions()

    return transaction, 201