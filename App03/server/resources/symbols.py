import flask_restful as restful

class Symbols(restful.Resource):
  def __init__(self, **kwargs):
    self.symbols = kwargs['symbols']
  
  def get(self):
    return self.symbols
