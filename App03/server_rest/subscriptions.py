from threading import Thread

from flask_restful import Resource
from flask import request

from server_rest.util.requests import abort_if, ERRORS, verify, format_sse

class SubscriptionsView(Resource):
  subscriptions = {}
  def __init__(self, symbols, announcers):
    self.available_symbols = symbols
    self.announcers = announcers

    Thread(target=self.check_subscriptions, daemon=True).start()

  def get(self, id):
    if id not in self.subscriptions:
      self.subscriptions[id] = {}
    return {'data': self.subscriptions[id]}

  def put(self, id):
    if id not in self.subscriptions:
      self.subscriptions[id] = {}
    subscription = verify(request, self.available_symbols)
    s = subscription.get('symbol')
    lower = subscription.get('lower')
    upper = subscription.get('upper')
    self.subscriptions[id][s] = {'lower': lower, 'upper': upper}
    return subscription, 201

  def check_subscriptions(self):
    # Thread para verificar eventos e notificar se necessario
    while True:
      for id, subscriptions in list(self.subscriptions.items()):
        for symb, limits in list(subscriptions.items()):
          quote = self.available_symbols[symb]
          if quote < float(limits['lower']) or quote > float(limits['upper']):
            msg = format_sse(f"{symb} reached {quote}")
            # Envia a mensagem para a fila de mensagens do cliente 'id'
            self.announcers[id].announce(msg)
            del self.subscriptions[id][symb]


