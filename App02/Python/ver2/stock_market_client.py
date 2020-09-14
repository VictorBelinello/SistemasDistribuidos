import Pyro4

class StockMarketClient:
  def __init__(self, name):
    """Identificado único do cliente"""
    self.id = id(self)
    """Nome do cliente"""
    self.name = name
    """Lista(sem repetições) de ações de interesse do cliente. Os elementos são do tipo Company"""
    self.quotes = set()
    """Lista de ações sobre as quais o cliente deseja ser notificado de modo assíncrono"""
    self.subscriptions = []
    """Referência para objeto remoto StockMarket. Preenchida através do método linkStockMarket"""
    self.market = None

  @Pyro4.expose
  @Pyro4.callback
  def notify(self, message):
    print("Notificação do servidor: {}".format(message))

  def __str__(self):
    return "{}".format(self.name)

  def __repr__(self):
    return str(self)
    
  def addQuote(company):
    self.quotes.add(company)

  def removeQuote(company):
    try:
      self.quotes.remove(company)
      print("Item removido.")
    except KeyError as e:
      print("Item não existia, sem alterações.")

  """Retorna uma lista de tuplas contendo as empresas e respectivos valores das ações."""
  def getQuotes(self):
    return [ (company.name, company.stock_value) for company in self.quotes ]

  def linkStockMarket(self, market):
    self.market = market
    market.linkClient(self)

  def getAllCompanies(self):
    companies = self.market.companies
    for company in companies:
      print(company.name, company.stock_value)

  def getCompanyIfExists(self, company_name):
    companies = self.market.companies
    for company in companies:
      if company.name == company_name:
        return company
    return None

if __name__ == "__main__":
    c = StockMarketClient("victor")
    print(c)
    print(c.id)