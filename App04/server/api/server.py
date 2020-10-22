from typing import Dict

from flask_restful import  Resource
from flask import request

from api.clientModel import ClientModel
from api.clientController import ClientController
from api.market import Market
from api.brokerModel import BrokerModel
from api.transaction import Transaction

class BrokerServer(object):
  # Normalmente esse recurso ficaria em outro servidor, mas para facilitar aqui esta tudo junto, apenas separado em classes
  def __init__(self, brokers : Dict[str, BrokerModel]):
    self.brokers = brokers
  
  def get(self):
    """GET request para /brokers"""
    res = []
    for broker in self.brokers.values():
      res.extend( broker.orders )
    return {'data': res}
  
  def add_transaction(self):
    """PUT request para /brokers"""
    json : dict = request.get_json()
    t = Transaction(json.get('buyer'), json.get('seller'), json.get('order'))
    buyer = self.brokers.get(json.get('buyer'))
    buyer.add_transaction(t)

    seller = self.brokers.get(json.get('seller'))
    seller.add_transaction(t)

    return {'data': json}

  def prepare_transaction(self, id : str):
    json : dict = request.get_json()
    # O coordenador esta enviando put request para um broker especifico (o outro participante)
    target_broker = self.brokers.get(id)
    print(f"{target_broker.client_id} should prepare transaction {json.get('tid')}")
    # Agora os dois brokers tem a transacao na lista e o protocolo pode iniciar
    return {'data': json}

class Server(Resource):
  """Recurso REST fornecido, recebe e trata as requisições HTTP.
  Efetivamente direciona o tratamento para o controller responsável pelo cliente."""
  clients : Dict[str, ClientController] = {}
  brokers : Dict[str, BrokerModel] = {}
  brokerServer : BrokerServer = BrokerServer(brokers)
  def __init__(self, market : Market):
    self.market = market

  def get(self, client_id : str, topic : str = "") -> dict:
    """Chamado quando recebe GET request"""
    if request.path == "/brokers":
      # Request interno
      return self.brokerServer.get()
    if topic == "":
      # Quando topic == "" supoe que eh primeiro request e precisa iniciar novo cliente
      if client_id not in self.clients:
        # So inicia se ainda nao estiver no dicionario
        model = ClientModel(client_id, self.market)
        self.clients[client_id] = ClientController(model)
        self.brokers[client_id] = self.clients[client_id].model.broker
        return {'data': self.market.symbols}
      else:
        # Esse request nao deveria ser feito mais de 1 vez
        return {}
        
    client : ClientController = self.clients[client_id]
    return client.get(topic)

  def put(self, client_id : str, topic : str = "" ) -> dict:
    """Chamado quando recebe PUT request"""
    if request.path == "/brokers":
      return self.brokerServer.add_transaction()
    if request.path.startswith("/brokers"):
      return self.brokerServer.prepare_transaction(topic)
    client : ClientController = self.clients[client_id]
    return client.put(topic)

  def delete(self, client_id : str, topic : str) -> dict:
    """Chamado quando recebe DELETE request"""
    client : ClientController = self.clients[client_id]
    return client.delete(topic)