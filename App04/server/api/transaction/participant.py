from threading import Lock
import os
from .transaction import Transaction

class Participant(object):
  def __init__(self, client_id : str, transactions : dict, stocks : list):
    self.client_id = client_id
    self.transactions = transactions
    self.transactions_lock = Lock()
    self.stocks = stocks
    self.stocks_lock = Lock()
    self.filename : str = f'data/CarteiraFinal_Acionista_{self.client_id}.txt'
    self.logfile : str = f'data/Log_Transacoes_Participante.txt'

    if os.path.exists(self.logfile):
      os.remove(self.logfile)

    self.FAKE_ABORT = True

  def add_transaction(self, t : Transaction):
    with self.transactions_lock:
      self.transactions[t.tid] = t

  def save_log(self, log : str):
    print(f"Saving {self.client_id} transaction log to file")
    with open(self.logfile, 'a') as f:
      f.write(log)
      f.write('\n')

  def save_stocks_to_file(self):
    print(f"Saving {self.client_id} stocks to file")
    with open(self.filename, 'w') as f:
      for stock in self.stocks:
        f.write(str(stock) + '\n')

  def load_previous_stocks(self):
    print(f"Loading {self.client_id} stocks from file")
    with open(self.filename, 'r') as f:
      backup = []
      for line in f.readlines():
        stock = eval(line)
        backup.append(stock)
      self.stocks = backup

  def prepare(self, tid : str) -> bool:
    try:
      self.transactions_lock.acquire()
      t : Transaction = self.transactions.get(tid)
      t.set_state('active')
      self.save_log( t.log())
      print(f"{self.client_id} Preparing transaction {t.tid}")
      
      self.save_stocks_to_file()
      
      self.stocks_lock.acquire()
      if t.seller == self.client_id:
        # Vendendo acoes
        self.sell_stocks(t.order)
      else:
        # Comprando acoes
        self.buy_stocks(t.order)
      t.set_state('temp commit')
      self.save_log(t.log())
      if self.FAKE_ABORT:
        self.FAKE_ABORT = False
        return False
      return True
    except Exception:
      return False
    

  def commit(self, tid : str):
    print("Commiting transaction")
    try:
      t : Transaction = self.transactions.get(tid)
      t.set_state('committed')
      self.save_log(t.log())
      self.save_stocks_to_file()
      self.cleanup_transaction(tid)
      return True
    except Exception:
      return False
    

  def abort(self, tid : str):
    print("Aborting transaction")
    try:
      t : Transaction = self.transactions.get(tid)
      t.set_state('aborted')
      self.save_log(t.log())
      self.load_previous_stocks()
      self.cleanup_transaction(tid)
      return True
    except Exception:
      return False

  def cleanup_transaction(self, tid : str):
    t : Transaction = self.transactions.pop(tid)
    for order in self.orders:
      if list(order[1:-2]) == list(t.order):
        self.orders.remove(order)
    self.stocks_lock.release()
    self.transactions_lock.release()