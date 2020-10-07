import random
from server_rest.util.market import Market

def get_random_stocks(symbols):
  symbols = Market.get_random_symbols(symbols)
  stocks = {}
  for s in symbols:
    amount = random.randint(1, 5)
    stocks[s] = amount
  return stocks

def can_trade(sell, buy):
  return ( 
  sell['owner'] != buy['owner'] and 
  sell['symbol'] == buy['symbol'] and
  sell['amount'] == buy['amount'] and
  sell['price'] == buy['price'] )