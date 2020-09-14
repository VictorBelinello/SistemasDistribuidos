from threading import Thread
from time import sleep
import random 
import Pyro4


@Pyro4.expose
class Company:
  MIN_STOCK_VALUE = 5
  MAX_STOCK_VALUE = 200
  """Tupla contendo todas as instâncias, usada para aplicar alteração de valor de ações de maneira automática"""
  _instances = ()
  _update_thread_running = False
  _pyro_daemon_running = False
  _update_thread = None

  def __init__(self, name="Default"):
    """Nome identificador da empresa"""
    self._name = name

    """Valor da ação da empresa, inicia com um valor aleatorio entre MIN_STOCK_VALUE e MAX_STOCK_VALUE"""
    self._stock_value = round( random.uniform(Company.MIN_STOCK_VALUE, Company.MAX_STOCK_VALUE), 2 )

    """Flag indicando se o valor da ação se alterou desde a ultima vez"""
    self._value_changed = False

    """Recria tupla com a nova instância. Ao usar tuplas ao invés de lista o valor não pode ser alterado fora desse construtor."""
    Company._instances = (Company._instances + (self, ))

    """Inicia thread de atualização de valores de ações se ainda não estiver rodando"""
    if not Company._update_thread_running:
      Company._update_thread = Thread(target=Company.updateQuotes, daemon=True).start()
      Company._update_thread_running = True

    self.daemon = Pyro4.Daemon()
    self.daemon.register(self)
    Thread(target=self.daemon.requestLoop, daemon=True).start()

  def __str__(self):
    return "{}\n".format(self._name)

  def __repr__(self):
    return "{}".format(self._name)
  
  
  @property
  def name(self):
    return self._name
  @property
  def stock_value(self):
    return self._stock_value

  @staticmethod
  def getDefaultCompanies():
    names = ["AAPL", "CSCO", "MSFT", "GOOG", "IBM", "HPQ", "BP"]
    companies = [Company(name) for name in names ]
    return companies

  """Função responsável por emular mudanças nos valores das ações. Todo o comportamento é pseudo-aleatório."""
  @classmethod
  def updateQuotes(cls):
    MIN_SLEEP = 2
    MAX_SLEEP = 5
    while True:
      for instance in cls._instances:
        instance._stock_value = round( random.uniform(cls.MIN_STOCK_VALUE, cls.MAX_STOCK_VALUE), 2 )
        instance._value_changed = True
      sleep( random.randint(MIN_SLEEP, MAX_SLEEP) )

if __name__ == "__main__":
  companies = Company.getDefaultCompanies()
  [print(c.stock_value) for c in companies]
  sleep(5)
  [print(c.stock_value) for c in companies]