import os
import subscription as StockSubscription
import company as StockCompany

import Pyro5.api

class StockClient(object):  
  def __init__(self, name):
    self._name = name
        
    self.stocks_owned = []

    self.stock_market = None

  @Pyro5.api.expose
  @property
  def name(self):
    return self._name

  def __str__(self):
    return f"{id(self)} {self.name}"

  ###############################################################
  def notifyEvent(self, message):
    print(f"\nNotificação : {message}\n")

  def notifyTransaction(self, type, company, amount, value):
    company_name = company['name']
    if type == StockCompany.BUY_STOCK_TYPE:
      # Comprou ações, precisa aumentar amount
      print(f"Comprou {amount} ações de {company_name} pagando {value}")
      flag = False
      for stock in self.stocks_owned:
        if stock['company']['name'] == company_name:
          stock['amount'] += amount
          flag = True
          break
      # Nao encontrou a empresa na lista de ações 
      # Significa que comprou ação de uma empresa nova, adiciona ela na lista
      if not flag:
        stock = StockCompany.createStock(company, amount)
        self.stocks_owned.append(stock)

    elif type == StockCompany.SELL_STOCK_TYPE:
      # Vendeu ações, precisa diminui amount
      print(f"Vendeu {amount} ações de {company_name} ganhando {value}")
      for stock in self.stocks_owned:
        if stock['company']['name'] == company_name:
          stock['amount'] -=  amount
          if stock['amount'] == 0:
            self.stocks_owned.remove(stock)

  ###############################################################
  def getCompanyQuotes(self):
    quotes = self.stock_market.getCompanyQuotesFor(self.name)
    for c in quotes:
      StockCompany.printCompany(c)

  def addCompanyQuote(self):
    company = StockCompany.getCompanyFromUser(self.stock_market)
    self.stock_market.addCompanyQuoteFor(self.name, company)

  def removeCompanyQuote(self):
    company = StockCompany.getCompanyFromUser(self.stock_market)
    self.stock_market.removeCompanyQuoteFor(self.name, company)

  ###############################################################
  def addSubscriptions(self):
    subscription = StockSubscription.getSubscriptionFromUser(self.stock_market)
    StockSubscription.printSubscription(subscription)
    self.stock_market.addSubscriptionFor(self.name, subscription)

  ###############################################################
  def getStocks(self):
    stocks = self.stocks_owned
    for s in stocks:
      StockCompany.printStock(s)

  def addDebugTransaction(self, base, type):
    stock_transaction = StockCompany.getDebugTransaction(base, type)
    print("Debugando")
    StockCompany.debug(stock_transaction)
    if stock_transaction['type'] == StockCompany.SELL_STOCK_TYPE:
      # Se não tiver imprime o aviso e retorna
      if not StockCompany.canDoStockTransaction(stock_transaction, self.stocks_owned):
        print("Transação de ações falhou")
        StockCompany.printStock(stock_transaction)
        print(f"Você não tem ações de {stock_transaction['company']['name']} suficientes para vender")
        return 
    self.stock_market.addStockTransactionFor(self.name, stock_transaction)
        
    self.stock_market.checkStockTransactions()

  def addStockTransaction(self):
    stock_transaction = StockCompany.getStockTransactionFromUser(self.stock_market)
    # Se esta tentando vender uma ação, verifica se ele tem suficiente
    if stock_transaction['type'] == StockCompany.SELL_STOCK_TYPE:
      # Se não tiver imprime o aviso e retorna
      if not StockCompany.canDoStockTransaction(stock_transaction, self.stocks_owned):
        print("Transação de ações falhou")
        StockCompany.printStock(stock_transaction)
        print(f"Você não tem ações de {stock_transaction['company']['name']} suficientes para vender")
        return 
    self.stock_market.addStockTransactionFor(self.name, stock_transaction)
    # Como adicionou uma nova transação já chama o método do stock_market para verificar se ela pode ser efetivada
    self.stock_market.checkStockTransactions()

  def showMenu(self):
    menu = {
      0: exit,
      1: self.getCompanyQuotes,
      2: self.addCompanyQuote,
      3: self.removeCompanyQuote,
      4: self.addSubscriptions,
      5: self.getStocks,
      6: self.addStockTransaction,
    }
    opt = -1
    while opt != 0:
      # Limpa o terminal de acordo com o SO
      os.system('cls' if os.name == 'nt' else 'clear')
      print("Digite 1 para listar cotações")
      print("Digite 2 para inserir em sua lista cotações")
      print("Digite 3 para remover de sua lista cotações")
      print("Digite 4 para adicionar inscrição para evento")
      print("Digite 5 para listar ações")
      print("Digite 6 para comprar/vender ações")
      print("Digite 0 para sair")
      print("*"*30)

      opt = int(input("Opção: "))

      func = menu[opt]
      func()

      input("ENTER para continuar...")

  def addStockMarket(self, market):
    self.stock_market = market
    self.stocks_owned = StockCompany.giveRandomStocks(self.stock_market)
    self.stock_market.initClient(self)
    print(f"{self.name} se conectou com {market.name}")

if __name__ == "__main__":
    c = StockClient("Victor")
    print(c)