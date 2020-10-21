from random import randint
from ..market import Market

class BrokerModel(object):
  def __init__(self, market : Market):
    self.stocks = [(s, randint(1, 5)) for s in Market.get_random_symbols(market.symbols)]
