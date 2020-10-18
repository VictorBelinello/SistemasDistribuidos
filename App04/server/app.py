from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from server import Server
from market import Market

app = Flask(__name__)
CORS(app)
api = Api(app)

m = Market()

api.add_resource(Server,
                  '/<string:client_id>',
                  '/<string:client_id>/<string:topic>',
                  '/<string:client_id>/<string:topic>/listen',
                  resource_class_kwargs={'market': m})

if __name__ == "__main__":
  app.run(debug=True)