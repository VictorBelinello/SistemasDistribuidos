from flask_restful import Resource
from flask import request

from server_rest.util.requests import abort_if, ERRORS, verify

class InterestsView(Resource):
  interests = {}
  def __init__(self, symbols, transactions):
    self.available_symbols = symbols
    self.transactions = transactions

  def get(self, id):
    if id not in self.interests:
      self.interests[id] = {}
    
    for symb in self.interests[id]:
      self.interests[id][symb] = self.available_symbols[symb]
    
    from_stocks = {}
    for symb in self.transactions.clients_stocks[id]:
      from_stocks[symb] = self.available_symbols[symb]
    # Combina os dois dicts
    response = {**from_stocks, **self.interests[id]}
    return {'data': response}

  def put(self, id):
    if id not in self.interests:
      self.interests[id] = {}
    interest = verify(request, self.available_symbols)
    s = interest.get('symbol')
    self.interests[id][s] = -1
    return interest, 201

  def delete(self, id):
    if id not in self.interests:
      abort_if(ERRORS.RESOURCE_NOT_FOUND, f"You have no interests registered.")
    interest = verify(request, self.available_symbols)
    symb = interest.get('symbol')
    if symb not in self.interests[id]:
      abort_if(ERRORS.RESOURCE_NOT_FOUND, f"The symbol {symb} is not in your interests list.")
    del self.interests[id][symb]
    return '', 204