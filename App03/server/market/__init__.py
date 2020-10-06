import random
import threading
import time


def random_quote():
  """Retorna uma valor de cotação entre 5 e 150, com duas casas decimais."""
  return round( random.uniform(5, 150), 2)

class Market(object):
  """Simula o mercado de ações"""
  def __init__(self):
    self.symbols = {
      "AAPL":random_quote(),
      "INTC":random_quote(),
      "NVDA":random_quote(),
      "QCOM":random_quote(),
      "CSCO":random_quote(),
      "TSLA":random_quote(),
      "TSM" :random_quote(),
      "MSFT":random_quote(),
      "GOOG":random_quote()
    }
    threading.Thread(target=self.update_quotes, daemon=True).start()

  def quote(self, symb):
    return self.symbols[symb]

  def get_random_symbols(self):
    # Pega todos os simbolos disponiveis
    keys = list(self.symbols.keys())
    # Escolhe uma quantidade 
    k = random.randint(0, len(keys))
    # Escolhe k simbolos, sem repeticao
    #TODO:TIRAR DEPOIS
    k = len(keys)
    symbols = random.sample(keys, k=k)
    return symbols

  def update_quotes(self):
    wait_time_max = 2
    while True:
      symbols = self.get_random_symbols()
      for s in symbols:
        # Escolhe uma cotação
        val = random_quote()
        # Atualiza valor
        self.symbols[s] = val
      # Espera tempo antes de atualizar novamente
      time.sleep(wait_time_max)

default_market = Market()

from flask import Blueprint

market_bp = Blueprint("market", __name__)

from . import views
