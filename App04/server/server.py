from flask_restful import Resource
from flask import request
from broker import Broker
from market import Market


class Server(Resource):
  """Recurso REST fornecido, recebe e trata as requisições HTTP.
  Efetivamente direciona o tratamento para o broker responsável pelo cliente."""
  clients_brokers : dict = {}
  def __init__(self, market : Market):
    self.market = market

  def get(self, client_id : str, topic : str = "") -> dict:
    """Chamado quando recebe GET request"""
    if request.path == f'/{client_id}':
      if client_id not in self.clients_brokers:
        # Primeiro request do cliente, usa como um init
        self.clients_brokers[client_id] = Broker(client_id, self.market)
        return {'data': self.market.symbols}
      else:
        return {}
    # Pega a ultima palavra apos /
    # Possivelmente listen
    last_param : str = request.path.split('/')[-1]
    broker : Broker = self.clients_brokers[client_id]
    return broker.get(topic, last_param)

  def put(self, client_id : str, topic : str) -> dict:
    """Chamado quando recebe PUT request"""
    broker : Broker = self.clients_brokers[client_id]
    return broker.addTo(topic, request.get_json())

  def delete(self, client_id : str, topic : str) -> dict:
    """Chamado quando recebe DELETE request"""
    broker : Broker = self.clients_brokers[client_id]
    return broker.removeFrom(topic, request.get_json())