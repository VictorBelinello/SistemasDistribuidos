from threading import Thread
from time import sleep

from server_rest.util.requests import format_sse
from server_rest.util.stocks import can_trade

class Transactions(object):
  transactions = {
    'buy': [],
    'sell': []
  }
  clients_stocks = {}

  def __init__(self, symbols, announcers):
    self.available_symbols = symbols
    self.announcers = announcers
    Thread(target=self.update_timers, daemon=True).start()

  def get_transactions(self, type, id):
    transactions = [t for t in self.transactions[type] if t['owner'] == id]
    return transactions

  def remove_stocks(self, target, symb, amount):
    new_amount = self.clients_stocks[target][symb] - amount
    if new_amount > 0 :
      self.clients_stocks[target][symb] = new_amount
    else:
      del self.clients_stocks[target][symb]

  def add_stocks(self, target, symb, amount):
    if symb in self.clients_stocks[target]:
      self.clients_stocks[target][symb] += amount
    else:
      self.clients_stocks[target][symb] = amount

  def trade(self, sell, buy):
    seller = sell['owner']
    buyer = buy['owner']

    symb = sell['symbol']
    amt = int(sell['amount'])
    total = float(sell['price']) * amt

    self.remove_stocks(seller, symb, amt)
    self.add_stocks(buyer, symb, amt )

    # Notifica envolvidos
    sell_msg = format_sse(f"You sold {amt} stocks of {symb}. Total:{total} ")
    buy_msg = format_sse(f"You bought {amt} stocks of {symb}. Total:{total} ")

    self.announcers[seller].announce(sell_msg)
    self.announcers[buyer].announce(buy_msg)

  def check_transactions(self):
    selling = self.transactions['sell']
    buying = self.transactions['buy']
    for sell in selling:
      for buy in buying:
        if can_trade(sell, buy):
          # Realiza a transacao
          self.trade(sell, buy)
          # Remove transacao das listas
          selling.remove(sell)
          buying.remove(buy)

  def update_timers(self):
    # Para efeito de demonstração aqui a unidade de tempo minima é um segundo
    # Se TIME_UNITY_SECONDS fosse 60, a unidade de condition_timeout seria minutos e assim por diante
    TIME_UNITY_SECONDS = 1
    while True:
      for type in ['sell', 'buy']:
        for t in self.transactions[type]:
          t['timeout'] = (t['timeout'] - 1) if t['timeout'] > 0 else 0
          if t['timeout'] == 0:
            # Se acabou o timer retira transação e avisa o cliente
            msg = format_sse(f"Transaction of {t['amount']} stocks from {t['symbol']} timeout! Removing")
            self.announcers[t['owner']].announce(msg)
            self.transactions[type].remove(t)
      sleep(TIME_UNITY_SECONDS)