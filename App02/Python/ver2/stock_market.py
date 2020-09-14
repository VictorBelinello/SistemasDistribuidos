import Pyro4
import sys
sys.path.append(".")
from stock_market_company import Company

@Pyro4.expose
class StockMarket:
  def __init__(self, companies=Company.getDefaultCompanies()):
    """Lista de objetos Company"""
    self._companies = companies
    """Lista de objetos StockMarketClient"""
    self._clients = []
  
  def linkClient(self, client):
    print("Linked successfully")
    self._clients.append(client)

  @Pyro4.oneway
  def notifyClient(self, client):
    try:
      client.notify()
    except Exception as e:
      print("Erro notifyClient")
      print(e)
      exit()

  @property
  def companies(self):
    return self._companies    

if __name__ == "__main__":
    sm = StockMarket()
    print(sm.companies)
