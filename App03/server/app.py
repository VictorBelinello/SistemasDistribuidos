import flask_restful as restful
from flask import Flask, request
from flask_cors import CORS

from resources.interests import Interests
from resources.symbols import Symbols
from common.market import Market

if __name__ == "__main__":
  app = Flask(__name__)
  #CORS(app)
  
  api = restful.Api(app)

  # Instancia um mercado de acoes
  market = Market()

  api.add_resource(Symbols, 
                    '/', # Get para '/' retorna todos os simbolos disponiveis
                    resource_class_kwargs={'symbols':market.symbols })

  base_clients_url = '/clients/<string:id>'
  base_url_interests = base_clients_url + '/interests'
  api.add_resource(Interests,
                    base_url_interests,
                    resource_class_kwargs={'symbols':market.symbols }) # Passa os simbolos do mercado para o recurso

  base_url_subscriptions = base_clients_url + '/subscriptions'

  app.run(debug=True)
