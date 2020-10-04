import flask_restful as restful
import random

def random_quote():
    return round( random.uniform(5, 150), 2)

class StockMarket(restful.Resource):
    symbols = {
        "AAPL":random_quote(),
        "INTC":random_quote(),
        "NVDA":random_quote(),
        "QCOM":random_quote(),
        "CSCO":random_quote(),
        "TSLA":random_quote(),
        "TSM" :random_quote(),
        "MSFT":random_quote(),
        "GOOG":random_quote()
    }
    def get(self): # Chamado quando recebe um HTTP GET para as rotas desse recurso
        return StockMarket.symbols