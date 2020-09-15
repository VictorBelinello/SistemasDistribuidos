import company as StockCompany
import stock as Stock
from client import StockClient
from threading import Thread
from time import sleep
from random import randint

class StockMarket(object):
  def __init__(self, name, companies):
    self.name = name
    print(f"Inicializando StockMarket {self.name}")
    # Empresas pertencente a bolsa, cada empresa é um dicionario, detalhes em company.py
    self.companies = {}

    # Dicionario contendo as ações da empresa sendo transacionadas
    # Separadas por venda e compra
    self.stocks_available = {}

    for company in companies:
      self.companies[company['name']] = company
      self.stocks_available[company['name']] = {'buying': [], 'selling': []}

    # Dicionário contendo as listas cotações dos clientes
    self.clients_quotes = {}
    # Dicionário contendo as inscrições para eventos dos clientes
    self.clients_subscriptions = {}
    # Dicionário contendo referências para clientes
    self.clients = {}

    Thread(target=self.updateCompaniesQuotes, daemon=True).start()

    Thread(target=self.updateTransactionsTimers, daemon=True).start()


  def __str__(self):
    companies_names = [c['name'] for c in self.companies.values()]
    return f"{self.name} contém as seguintes empresas: {companies_names}"

  def initClient(self, client):
    self.clients_quotes[client.name] = []
    self.clients_subscriptions[client.name] = []
    self.clients[client.name] = client

###############################################################
  def getCompanyQuotesFor(self, name):
    return self.clients_quotes[name]

  def addCompanyQuoteFor(self, name, company):
    quotes = self.clients_quotes[name]
    quotes.append( company )

  def removeCompanyQuoteFor(self, name, company):
    quotes = self.clients_quotes[name]
    try:
      quotes.remove(company)
    except ValueError:
      print("Empresa não estava na lista, nada feito.")
    

###############################################################
  def addSubscriptionFor(self, name, subscription):
    subscriptions = self.clients_subscriptions[name]
    subscriptions.append(subscription)

  def checkSubscriptions(self):
    for client_name, subscriptions in self.clients_subscriptions.items():
      client = self.clients[client_name]
      for sub in subscriptions:
        for company in self.companies.values():
          # Empresa "alvo" da inscrição
          if company == sub['company']:
            # Verifica os limites
            value = company['stock_value']
            if value <= sub['lower_limit']:
              message = f"{company['name']} atingiu o valor R${value} ficando abaixo do limite de {sub['lower_limit']}"
              client.notifyEvent(message)
            if  value >= sub['upper_limit']:
              message = f"{company['name']} atingiu o valor R${value} ficando acima do limite de {sub['upper_limit']}"
              client.notifyEvent(message)


###############################################################  
  def addStockTransactionFor(self, client_name, stock_transaction):
    #TODO
    company_name = stock_transaction['company']['name']
    stock_type = stock_transaction['type']
    transaction_type = "buying" if stock_type == Stock.BUY_STOCK_TYPE else "selling"
    stock_available = (self.clients[client_name], stock_transaction)
    self.stocks_available[company_name][transaction_type].append(stock_available)
    #client.stocks_owned.append(stock_transaction)

  def checkStockTransactions(self):
    for company in self.companies.values():
      name = company['name']
      # Verifica as ações da empresa "name" sendo vendidas
      for selling_stock in self.stocks_available[name]["selling"]:
        # Pega a referencia para o objeto StockClient vendedor
        seller = selling_stock[0]
        # Pega as informações da transação de venda armazenadas no dicionário stock
        sell_transaction = selling_stock[1]
        for buying_stock in self.stocks_available[name]["buying"]:
          # Pega a referencia para o objeto StockClient vendedor
          buyer = buying_stock[0]
          # Pega as informações da transação de compra armazenadas no dicionário stock
          buy_transaction = buying_stock[1]
          
          # So vendo se for a mesma quantidade para facilitar o código
          if sell_transaction['amount'] == buy_transaction['amount']:
            # Situação onde transação ocorre direto:
            # Preço de venda <= Preço de compra
            if sell_transaction['target_price'] <= buy_transaction['target_price']:
              buy_transaction['target_price'] = sell_transaction['target_price']
              self.doTransaction(company, selling_stock, buying_stock)
              return
            # Preço de venda > Preço de compra
            else:
              # Verifica se timer de estado condicional ainda esta ativo
              sell_timer = sell_transaction['conditional_timeout'] > 0
              buy_timer = buy_transaction['conditional_timeout'] > 0
              # Os dois timers estão ativos
              if sell_timer and buy_timer:
                # Transação não ocorre, pois os timers ainda estão ativos e preços não são "corretos"
                return
              # Um dos timers não está mais ativo
              else:
                # Lembrando que nesse ponto Preço de venda > Preço de compra
                # IMPORTANTE: A ordem dos ifs favorece os compradores em caso de ambos estarem com timers desativados
                # Timer do vendedor não está mais ativo
                if not sell_timer:
                  # Diminui valor de venda para o valor de compra disponível
                  sell_transaction['target_price'] = buy_transaction['target_price']
                  self.doTransaction(company, selling_stock, buying_stock)
                # Timer do comprador não está mais ativo
                else:
                  # Sobe o valor de compra para o valor de venda disponível
                  buy_transaction['target_price'] = sell_transaction['target_price']
                  self.doTransaction(company, selling_stock, buying_stock)

  def doTransaction(self, company, selling_stock, buying_stock):
    print("Realizando transação: ")
    print(f"Vendedor: {selling_stock[0].name} Comprador: {buying_stock[0].name}")
    # Atualiza os clientes sobre suas transações
    self.updateTransactionClients(company, selling_stock, buying_stock)
    # Remove as transações das listas 
    self.stocks_available[company['name']]['buying'].remove(buying_stock)
    self.stocks_available[company['name']]['selling'].remove(selling_stock)

  def updateTransactionClients(self, company, selling_stock, buying_stock):
    seller, sell_transaction = selling_stock
    sell_value = round(sell_transaction['amount'] * sell_transaction['target_price'], 2)
    seller.notifyTransaction(sell_transaction['type'], company, sell_transaction['amount'], sell_value)

    buyer, buy_transaction = buying_stock
    buy_value = round(buy_transaction['amount'] * buy_transaction['target_price'], 2)
    buyer.notifyTransaction(buy_transaction['type'], company, buy_transaction['amount'], buy_value)


###############################################################
  def getAllCompanies(self):
    return [c for c in self.companies.values()]

  def updateCompaniesQuotes(self):
    """Função responsável por emular mudanças nos valores das ações.
    Todo o comportamento é pseudo-aleatório."""
    MIN_SLEEP = 2
    MAX_SLEEP = 5
    while True:
      for company in self.companies.values():
        #printCompany(company)
        company['stock_value'] = Stock.getRandomStockValue()
      self.checkSubscriptions()
      sleep(randint(MIN_SLEEP, MAX_SLEEP))
  
  def updateTransactionsTimers(self):
    # Para efeito de demonstração aqui a unidade de tempo minima é um segundo
    # Se TIME_UNITY_SECONDS fosse 60, a unidade de condition_timeout seria minutos e assim por diante
    TIME_UNITY_SECONDS = 1
    while True:
      for names in self.companies:
        # Percorre os pedidos de compra
        for stock in self.stocks_available[names]['buying']:
          transaction = stock[1]
          if transaction['conditional_timeout'] > 0:
            # Remove uma unidade de tempo
            transaction['conditional_timeout'] -= 1
          else:
            # Timer acabou, agora alguma transação que antes não era possível pode ser feita
            # Verifica transações
            self.checkStockTransactions()
        # Percorre os pedidos de venda
        for stock in self.stocks_available[names]['selling']:
          transaction = stock[1]
          if transaction['conditional_timeout'] > 0:
            # Remove uma unidade de tempo
            transaction['conditional_timeout'] -= 1
          else:
            # Timer acabou, agora alguma transação que antes não era possível pode ser feita
            # Verifica transações
            self.checkStockTransactions()
      # Espera TIME_UNITY_SECONDS segundos antes de diminuir novamente
      sleep(TIME_UNITY_SECONDS)
