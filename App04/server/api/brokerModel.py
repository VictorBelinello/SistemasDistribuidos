from random import randint
from typing import Optional
from threading import Lock
import requests
import os

from .market import Market
from .transaction.transaction import Transaction
from .transaction.participant import Participant
from .brokerInterface import BrokerInterface

class BrokerModel(Participant):
  """Classe para representar um broker, responsavel pelas acoes do cliente e por realizar transacoes"""
  def __init__(self, client_id : str, market : Market):
    self.client_id : str = client_id
    self.stocks : list = [[s, randint(1, 5)] for s in Market.get_random_symbols(market.symbols)]
    self.orders : list = []
    self.transactions : dict = {}
    super().__init__(self.client_id, self.transactions, self.stocks)
    self.interface = BrokerInterface()
   
  
  def sell_stocks(self, order : tuple):
    print("Selling stocks")
    symbol = order[0]
    amount = order[2]
    print(self.stocks)
    for stock in self.stocks:
      if stock[0] == symbol:
        stock[1] -= amount
        if stock[1] == 0:
          self.stocks.remove(stock)
    print(self.stocks)

  def buy_stocks(self, order : tuple):
    print("Buying stocks")
    symbol = order[0]
    amount = order[2]
    found = False
    for stock in self.stocks:
      if stock[0] == symbol:
        stock[1] += amount
        found = True
    if not found:
      stock = (symbol, amount)
      self.stocks.append( stock )

  def begin_transaction(self, tid : str):
    # Chamada pelo BrokerServer apos receber PUT request para nova transacao
    # self eh um comprador sempre
    self.logfile = self.logfile.replace('Participante', 'Coordenador')
    t : Transaction = self.transactions.get(tid)
    # Envia notificacao para preparar para commit 
    seller_vote = self.interface.send_can_commit(t.seller, t.tid)
    # Prepara a propria transacao
    my_vote = self.prepare(t.tid)
    if seller_vote and my_vote:
      # Ambos votaram sim, realiza commit
      seller_ack = self.interface.send_commit(t.seller, t.tid)
      my_ack = self.commit(t.tid)
    else:
      # Alguem votou nao, aborta
      self.interface.send_abort(t.seller, t.tid)
      self.abort(t.tid)
    # Volta logfile para ser apenas participante
    self.logfile = self.logfile.replace('Coordenador', 'Participante')

  def notify_trade(self, my : tuple, other : tuple):
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
        self.notify_trade(my_order, order)

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
