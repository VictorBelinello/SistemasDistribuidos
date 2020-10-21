from random import randint
from server.market import Market

class BrokerModel(object):
  def __init__(self, market : Market):
    self.stocks : list = [(s, randint(1, 5)) for s in Market.get_random_symbols(market.symbols)]
    self.orders : list = []

  def add_order(self, order : dict):
    self.orders.append(order)
