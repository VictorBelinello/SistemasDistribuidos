from typing import Dict

from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api, Resource

from api.clientModel import ClientModel
from api.clientController import ClientController
from api.market import Market

app = Flask(__name__)
CORS(app)
api = Api(app)

class Server(Resource):
  """Recurso REST fornecido, recebe e trata as requisições HTTP.
  Efetivamente direciona o tratamento para o controller responsável pelo cliente."""
  clients : Dict[str, ClientController] = {}
  def __init__(self, market : Market):
    self.market = market

  def get(self, client_id : str, topic : str = "") -> dict:
    """Chamado quando recebe GET request"""
    if request.path == '/brokers':
      # Um request interno feito pelo broker de um cliente para obter os outros
      # Normalmente seria feito para outro servidor
      res = []
      for controller in self.clients.values():
        res.extend( controller.model.broker.orders )
      return {'data': res}
    if topic == "":
      # Quando topic == "" supoe que eh primeiro request e precisa iniciar novo cliente
      if client_id not in self.clients:
        # So inicia se ainda nao estiver no dicionario
        model = ClientModel(client_id, self.market)
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

m = Market()

api.add_resource(Server,
                  '/<string:client_id>',
                  '/<string:client_id>/<string:topic>',
                  '/<string:client_id>/listen/<string:topic>',
                  resource_class_kwargs={'market': m})

if __name__ == "__main__":
  app.run(debug=True)