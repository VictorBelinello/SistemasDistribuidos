from datetime import datetime
import json

class Transaction(object):
  """Representa uma transacao. Tem um comprador, um vendedor e a ordem em si, contendo o simbolo, preco e quantidade"""
  TID = 1
  def __init__(self, buyer : str, seller : str, order : tuple ):
    self.buyer = buyer 
    self.seller = seller 
    self.order = order
    self.state = "ACTIVE"
    self.tid = Transaction.TID
    Transaction.TID += 1

  def __repr__(self):
    return str(self)

  def __str__(self):
    return f"T<{self.tid}> between B:{self.buyer} and S:{self.seller}. Order:{self.order}"


  def set_state(self, state : str):
    self.state = state.upper()
  def log(self):
    current_date = datetime.now().strftime("%d/%m/%Y %X")
    return f"{current_date}: {self.state} {self}"