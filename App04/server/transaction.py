from enum import Enum

class Transaction(object):
  TID = 1
  class State(Enum):
    IDLE = 0
    ACTIVE = 1
    TEMPORARY_COMMIT = 2
    COMMITED = 3
    FAILED = 4
    ABORTED = 5

  def __init__(self):
    self.state = Transaction.State.IDLE
    self.tid = Transaction.TID
    Transaction.TID += 1
  
  def __str__(self):
    return f"Transaction {self.tid}: <{self.state}>"

if __name__ == "__main__":
  t1 = Transaction()
  t2 = Transaction()
  t3 = Transaction()
  t4 = Transaction()
  print(t1, t2, t3, t4)
