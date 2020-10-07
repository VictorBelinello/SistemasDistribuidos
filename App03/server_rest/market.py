from flask_restful import Resource

class MarketView(Resource):
  def __init__(self, symbols):
    self.symbols = symbols

  def get(self):
    return {'data': self.symbols}
