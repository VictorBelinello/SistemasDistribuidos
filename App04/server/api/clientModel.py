from .market import Market
from .brokerModel import BrokerModel

class ClientModel(object):
  def __init__(self, client_id : str, market : Market):
    self.client_id = client_id
    self.market = market

    self.quotes : list = []
    self.subscriptions : list = []
    self.broker = BrokerModel(self.client_id, self.market)
  
  def check_symbol(self, symbol : str) -> bool:
    return symbol in self.market.symbols

  def check_subscriptions(self):
    # Chamado pelo clientController quando recebe GET para /listen/subscriptions
    # Retorna uma mensagem quando o evento inscrito ocorre
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
          
  ############# QUOTES
  def add_quote(self, symbol : str) -> tuple:
    if self.check_symbol(symbol):
      if symbol not in self.quotes:
        self.quotes.append( symbol )
        return (True, None)
      return (False, f"Symbol {symbol} already on your quotes")
    return (False, f"Couldn't find symbol {symbol} on market symbols")

  def get_quotes(self) -> dict:
    res = {}
    for symb in self.quotes:
      res[symb] = self.market.quote(symb)
    for stock in self.broker.stocks:
      symb = stock[0]
      res[symb] = self.market.quote(symb)
    return res

  def del_quote(self, symbol : str) -> tuple:
    if symbol in self.quotes:
      self.quotes.remove(symbol)
      return (True, None)
    return (False, f"Couldn't find symbol {symbol} on your quotes")

  ############# SUBSCRIPTIONS
  def add_subscription(self, symbol : str, lower : str, upper : str) -> tuple:
    if self.check_symbol(symbol):
      if not lower or not upper:
        return (False, f"Subscription not complete, missing limit")
      sub = (symbol, float(lower), float(upper))
      self.subscriptions.append( sub )
      return (True, None)
    return (False, f"Couldn't find symbol {symbol} on market symbols")

  def get_subscriptions(self) -> dict:
    res = {}
    for sub in self.subscriptions:
      symb = sub[0]
      lower = sub[1]
      upper = sub[2]
      res[symb] = (lower, upper)
    return res 

  ############# STOCKS
  def get_stocks(self) -> dict:
    res = {}
    for stock in self.broker.stocks:
      res[stock[0]] = stock[1]
    return res

  ############# ORDER
  def add_order(self, symbol : str, operation : str, price : float, amount : int, timeout : int) -> tuple:
    if self.check_symbol(symbol):
      if not price or not amount or not timeout:
        return (False, f"Order not complete, missing price, amount or timeout")
      if operation == 'buy' or operation == 'sell':
        return self.broker.add_order(symbol, operation, price, amount, timeout)
      else:
        return (False, f"Order operation should be either buy or sell. Got : {operation}")
    return (False, f"Couldn't find symbol {symbol} on market symbols")

  
