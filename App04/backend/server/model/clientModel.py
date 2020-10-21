from server.market import Market
from .brokerModel import BrokerModel

class ClientModel(object):
  def __init__(self, market : Market):
    self.market = market

    self.quotes : list = []
    self.subscriptions : list = []
    self.broker = BrokerModel(self.market)
    self.transactions : list = []
  
  def check_symbol(self, symbol : str) -> bool:
    return symbol in self.market.symbols

  def check_subscriptions(self):
    while True:
      if len(self.subscriptions):
        for sub in self.subscriptions:
          symb : str = sub[0]
          lower : float = sub[1]
          upper : float = sub[2]
          current : float = self.market.quote(symb)
          if current < lower or current > upper:
            msg : str = f"Symbol {symb} at {current}"
            self.subscriptions.remove(sub)
            yield f"data: {msg}\n\n"
          

  def add_quote(self, symbol : str) -> tuple:
    if self.check_symbol(symbol):
      if symbol not in self.quotes:
        self.quotes.append( symbol )
        return (True, None)
      return (False, f"Symbol {symbol} already on your quotes")
    return (False, f"Couldn't find symbol {symbol} on market symbols")

  def add_subscription(self, symbol : str, lower : str, upper : str) -> tuple:
    if self.check_symbol(symbol):
      if not lower or not upper:
        return (False, f"Subscription not complete, missing limit")
      sub = (symbol, float(lower), float(upper))
      self.subscriptions.append( sub )
      return (True, None)
    return (False, f"Couldn't find symbol {symbol} on market symbols")
  
  def get_quotes(self) -> dict:
    res = {}
    for symb in self.quotes:
      res[symb] = self.market.quote(symb)
    for stock in self.broker.stocks:
      symb = stock[0]
      res[symb] = self.market.quote(symb)
    return res

  def get_subscriptions(self) -> dict:
    res = {}
    for sub in self.subscriptions:
      res[sub[0]] = (sub[1], sub[2])
    return res 

  def get_stocks(self) -> dict:
    res = {}
    for stock in self.broker.stocks:
      res[stock[0]] = stock[1]
    return res

  def del_quote(self, symbol : str) -> tuple:
    if symbol in self.quotes:
      self.quotes.remove(symbol)
      return (True, None)
    return (False, f"Couldn't find symbol {symbol} on your quotes")

  def del_subscription(self, symbol : str, lower : str, upper : str) -> tuple:
    sub = (symbol, float(lower), float(upper))
    if sub in self.subscriptions:
      self.subscriptions.remove(sub)
      return (True, None)
    return (False, f"Couldn't find subscription {sub} on your subscriptions")

  
