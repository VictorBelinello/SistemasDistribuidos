import flask_restful as restful
from flask import Flask, request
from flask_cors import CORS

from views import StockMarket

if __name__ == "__main__":
    app = Flask(__name__)
    CORS(app)
    api = restful.Api(app)

    api.add_resource(StockMarket, '/symbols')

    app.run(debug=True)
