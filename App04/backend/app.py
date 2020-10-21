from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from server.server import Server
from server.market import Market

app = Flask(__name__)
app.url_map.strict_slashes = False

CORS(app)
api = Api(app)

m = Market()

api.add_resource(Server,
                  '/<string:client_id>/',
                  '/<string:client_id>/<string:topic>/',
                  '/<string:client_id>/listen/<string:topic>/',
                  resource_class_kwargs={'market': m})

if __name__ == "__main__":
  app.run(debug=True)