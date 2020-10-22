from random import randint
from typing import Optional
import requests

from .market import Market
from .transaction.transaction import Transaction

from .brokerInterface import BrokerInterface

class BrokerModel(object):
  """Classe para representar um broker, responsavel pelas acoes do cliente e por realizar transacoes"""
  def __init__(self, client_id : str, market : Market):
    self.client_id : str = client_id
    self.stocks : list = [(s, randint(1, 5)) for s in Market.get_random_symbols(market.symbols)]
    self.orders : list = []
    self.interface = BrokerInterface()
    self.transactions : dict = {}

  def add_transaction(self, t : Transaction):
    self.transactions[t.tid] = t
    if t.buyer == self.client_id:
      # Se eu for o comprador, vira o coordenador da transacao
      # prepare
      self.interface.send_prepare(t.seller, t.tid)
      # if ok commit
      # else abort
      
    print(self.transactions)

  def start_trade(self, my : tuple, other : tuple):
    order = my[1:-2]
    buyer = my[-1] if my[0] == 'buy' else other[-1]
    seller = my[-1] if my[0] == 'sell' else other[-1]

    self.interface.notify_brokers(order, buyer, seller)

  def check_orders(self, my_order : tuple):
    # Pega os outros brokers no sistema e ve se algum pode realizar uma transacao
    print("Checking if can make transaction")
    for order in self.interface.get_all_orders():
      if order[-1] == self.client_id:
        continue
      diff_operation = my_order[0] != order[0] # Um vendendo e outro comprando
      same_symbol = my_order[1] == order[1]    # Mesmo symbol
      same_price = my_order[2] == order[2]     # Mesmo preco
      same_amount =  my_order[3] == order[3]   # Mesma quantidade
      if diff_operation and same_symbol and same_price and same_amount:        
        self.start_trade(my_order, order)

  def add_order(self, symbol : Optional[str], operation : str , price : float, amount : int, timeout : int) -> tuple:
    try:
      if operation == 'sell':
        # Verifica se cliente tem acoes para vender
        owned : list = [s[1] for s in self.stocks if s[0] == symbol]
        if not owned or owned[0] < amount:
          # Nao tenhuma acao de 'symbol' ou nao tem quantidade suficiente
          raise AttributeError(0 if not owned else owned[0])
      order = (operation, symbol, float(price), int(amount), int(timeout), self.client_id)
      self.orders.append(order)
      self.check_orders(order)
      return (True, None)
    except AttributeError as a:
      return (False, f'You cannot make this order, you have {a.args[0]} stocks of {symbol}')
    except ValueError as v:
      print(v)
      return (False, 'Failed to convert one of the order parameters')
    except Exception as e:
      print(e)
      return (False, 'Something went wrong')
