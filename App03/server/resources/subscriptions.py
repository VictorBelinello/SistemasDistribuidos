import flask_restful as restful
from flask import request, Response

class Subscriptions(restful.Resource):
  subscriptions = {}
  def __init__(self, **kwargs):
    self.market_symbols = kwargs['symbols']

  def should_notify(self, id):
    for subscription in self.subscriptions[id]:
      symb = subscription['symbol']
      lower = subscription['lower']
      upper = subscription['upper']
      quote = self.market_symbols[symb] 
      if quote > upper or quote < lower:
        print("Should notify")
        return "Se liga mermao" 

  def notify(self, id):
    while True:
      yield f'data: {self.should_notify(id)}\n\n'

  def get(self, id):
    if id not in self.subscriptions:
      self.subscriptions[id] = []
    if request.path == f'/clients/{id}/subscriptions/stream':
      print("TEs")
      return Response(self.notify(id), mimetype="text/event-stream")
    return self.subscriptions[id]

  def post(self, id):
    if id not in self.subscriptions:
      self.subscriptions[id] = []

    symbol = request.form.get('symbol')
    if symbol not in self.market_symbols:
      return "Nothing done"

    self.subscriptions[id].append(request.form.to_dict())

    return f"Post subscription {symbol}"