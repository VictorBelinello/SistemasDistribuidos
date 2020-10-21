from typing import Dict

from flask_restful import Resource
from flask import request

from .model.clientModel import ClientModel
from .controller.clientController import ClientController
from .market import Market

class Server(Resource):
  """Recurso REST fornecido, recebe e trata as requisições HTTP.
  Efetivamente direciona o tratamento para o broker responsável pelo cliente."""
  clients : Dict[str, ClientController] = {}
  def __init__(self, market : Market):
    self.market = market

  def get(self, client_id : str, topic : str = "") -> dict:
    """Chamado quando recebe GET request"""
    if topic == "":
      # Quando topic == "" supoe que eh primeiro request e precisa iniciar novo cliente
      if client_id not in self.clients:
        # So inicia se ainda nao estiver no dicionario
        model = ClientModel(self.market)
        self.clients[client_id] = ClientController(model)
        return {'data': self.market.symbols}
      else:
        # Esse request nao deveria ser feito mais de 1 vez
        return {}
        
    client : ClientController = self.clients[client_id]
    return client.get(topic)

  def put(self, client_id : str, topic : str) -> dict:
    """Chamado quando recebe PUT request"""
    client : ClientController = self.clients[client_id]
    return client.put(topic)

  def delete(self, client_id : str, topic : str) -> dict:
    """Chamado quando recebe DELETE request"""
    client : ClientController = self.clients[client_id]
    return client.delete(topic)