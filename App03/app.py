from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api

app = Flask(__name__)
CORS(app)
api = Api(app)

from server_rest.market import MarketView
from server_rest.util.market import Market

from server_rest.interests import InterestsView
from server_rest.subscriptions import SubscriptionsView
from server_rest.util.announcer import AnnouncerView

from server_rest.transactions import TransactionsView
from server_rest.util.transactions import Transactions

m = Market()
# Dicionario compartilhado pelas views que precisam anunciar mensagens
# Ou seja Subscriptions e Transactions
# As chaves sao os ids dos usuarios
announcers = {}

api.add_resource(MarketView, '/',
resource_class_kwargs={'symbols': m.symbols})

api.add_resource(InterestsView, '/interests/<string:id>',
resource_class_kwargs={'symbols': m.symbols})

api.add_resource(SubscriptionsView, '/subscriptions/<string:id>',
resource_class_kwargs={'symbols': m.symbols, 'announcers': announcers})

transactions = Transactions(m.symbols, announcers)

base_route = '/transactions/<string:id>'
api.add_resource(TransactionsView, base_route, base_route + '/buy', base_route + '/sell',
resource_class_kwargs={'symbols': m.symbols, 'transactions': transactions})

api.add_resource(AnnouncerView, '/listen/<string:id>',
resource_class_kwargs={'announcers': announcers})

if __name__ == "__main__":
  app.run(debug=True)