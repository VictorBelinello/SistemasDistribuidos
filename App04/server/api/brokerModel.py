from random import randint
from typing import Optional
import requests

from .market import Market

class BrokerInterface(object):  
  # Faz a interface com outros brokers
  # Normalmente realizando requisicoes para outros servidores onde os brokers estao
  # Aqui faz a requisicao para o proprio servidor
  def __init__(self, client_id : str):
    self.client_id = client_id
    self.url = 'http://127.0.0.1:5000/brokers'

  def get_others(self) -> list:
    r = requests.get(self.url)
    # Recupera um json com um unico campo 'data'
    json : dict = r.json()
    # Esse campo contem um vetor de ordens, onde uma ordem eh tambem um vetor
    orders : dict = json['data']
    # O ultimo campo do vetor order(order[-1]) eh o id do cliente que postou a ordem
    return [order for order in orders if order[-1] != self.client_id]

class BrokerModel(object):
  def __init__(self, client_id : str, market : Market):
    self.client_id : str = client_id
    self.stocks : list = [(s, randint(1, 5)) for s in Market.get_random_symbols(market.symbols)]
    self.orders : list = []
    self.interface : BrokerInterface = BrokerInterface(self.client_id)


  def check_if_can_trade(self, other_order : tuple):
    for order in self.orders:
      if order[0] != other_order[0]:        # Um vendendo e outro comprando
        if order[1] == other_order[1]:      # Mesmo symbol
          if order[2] == other_order[2]:    # Mesmo preco
            if order[3] == other_order[3]:  # Mesma quantidade
              print(f"I can trade my {order} with {other_order}")

  def check_orders(self):
    # Pega os outros brokers no sistema e ve se algum pode realizar uma transacao
    print("Checking if can make transaction")
    for order in self.interface.get_others():
      self.check_if_can_trade(order)

  def add_order(self, symbol : Optional[str], operation : str , price : float, amount : int, timeout : int) -> tuple:
    try:
      if operation == 'sell':
        # Verifica se cliente tem acoes para vender
        owned : list = [s[1] for s in self.stocks if s[0] == symbol]
        if not owned or owned[0] < amount:
          # Nao tenhuma acao de 'symbol' ou nao tem quantidade suficiente
          raise AttributeError(0 if not owned else owned[0])
      order = [operation, symbol, float(price), int(amount), int(timeout), self.client_id]
      self.orders.append(order)
      self.check_orders()
      return (True, None)
    except AttributeError as a:
      return (False, f'You cannot make this order, you have {a.args[0]} stocks of {symbol}')
    except ValueError as v:
      print(v)
      return (False, 'Failed to convert one of the order parameters')
    except Exception as e:
      print(e)
      return (False, 'Something went wrong')
