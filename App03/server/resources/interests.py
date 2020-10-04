import flask_restful as restful
from flask import request 

class Interests(restful.Resource):
  interests = {}
  def __init__(self, **kwargs):
    self.market_symbols = kwargs['symbols']


  def make_response(self, symbs):
    response = {}
    for symb in symbs:
      response[symb] = self.market_symbols[symb]
    return response

  def get(self, id):
    if id not in self.interests:
      self.interests[id] = []
    return self.make_response(self.interests[id])

  def post(self, id):
    if id not in self.interests:
      self.interests[id] = []

    symbol = request.form.get("symbol")

    if symbol not in self.market_symbols:
      return "Nothing done"
    self.interests[id].append( symbol )
    return f"Post interest {symbol}"

  def delete(self, id):
    if id not in self.interests:
      return "Nothing done"

    symbol = request.form.get("symbol")

    if symbol not in self.interests[id]:
      return "Nothing done"
    self.interests[id].remove( symbol )
    return "Done"