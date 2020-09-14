import random
import time
import Pyro4

from stock import new_stock, print_stock

from threading import Thread

class StockMarketClient:
  def __init__(self, id, name):
    """Identificado único do cliente"""
    self.id = id
    """Nome do cliente"""
    self.name = name
    """Lista(sem repetições) de ações de interesse do cliente. Os elementos são do tipo Company"""
    self.quotes = set()
    """Lista de ações sobre as quais o cliente deseja ser notificado de modo assíncrono"""
    self.subscriptions = []
  
  def __str__(self):
    return "{}".format(self.name)

  def addQuote(company):
    self.quotes.add(company)

  def removeQuote(company):
    try:
      self.quotes.remove(company)
      print("Item removido.")
    except KeyError as e:
      print("Item não existia, sem alterações.")

  """Retorna uma lista de tuplas contendo as empresas e respectivos valores das ações."""
  def getQuotes():
    return [ (company.name, company.stock_value) for company in self.quotes ]

class Company:
  MIN_STOCK_VALUE = 5
  MAX_STOCK_VALUE = 200
  """Tupla contendo todas as instâncias, usada para aplicar alteração de valor de ações de maneira automática"""
  _instances = ()
  _update_thread_running = False
  _update_thread = None

  def __init__(self, name):
    """Nome identificador da empresa"""
    self.name = name

    """Valor da ação da empresa, inicia com um valor aleatorio entre MIN_STOCK_VALUE e MAX_STOCK_VALUE"""
    self.stock_value = round( random.uniform(Company.MIN_STOCK_VALUE, Company.MAX_STOCK_VALUE), 2 )

    """Flag indicando se o valor da ação se alterou desde a ultima vez"""
    self.value_changed = False

    """Recria tupla com a nova instância. Ao usar tuplas ao invés de lista o valor não pode ser alterado fora desse construtor."""
    Company._instances = (Company._instances + (self, ))

    """Inicia thread de atualização de valores de ações se ainda não estiver rodando"""
    if not Company._update_thread_running:
      Company._update_thread = Thread(target=Company.updateQuotes, daemon=True).start()

  def __str__(self):
    return "{}\n".format(self.name)

  @staticmethod
  def getDefaultCompanies():
    names = ["AAPL", "CSCO", "MSFT", "GOOG", "IBM", "HPQ", "BP"]
    companies = [Company(name) for name in names ]
    return companies

  """Função responsável por emular mudanças nos valores das ações. Todo o comportamento é pseudo-aleatório."""
  @classmethod
  def updateQuotes(cls):
    while True:
      for instance in cls._instances:
        instance.stock_value = round( random.uniform(cls.MIN_STOCK_VALUE, cls.MAX_STOCK_VALUE), 2 )
        instance.value_changed = True
      time.sleep( random.randint(5, 20) )
  
  
@Pyro4.expose
class StockMarket:
  def __init__(self, companies=Company.getDefaultCompanies()):
    """Lista de objetos Company"""
    self._companies = companies
    """Lista de objetos StockMarketClient"""
    self._clients = []

  def generate_quotes(self):
    while True: # Loop infito simulando variacoes de quotacoes
      # Percorre todas as empresas 
      for company in self._companies.keys():
        # Decide aleatoriamente se vai alterar o valor da acao da empresa
        if random.choice([True, False]):
          # Gera um valor aleatorio para acao entre 5 e 200 arredondado para 2 casas
          self._companies[company]["value"] = round( random.uniform(5, 200), 2 ) 
          self._companies[company]["changed"] = True

      self.check_notify_requests()
      # Espera um tempo aleatorio entre 5 e 25 segundos para continuar
      time.sleep( random.randint(5, 20) ) 

  @property
  def companies(self):
    result = []
    for k in self._companies:
      value = self._companies[k]["value"]
      result.append( (k, value) )
    return result

  def check_limits(self, client_obj, company):
    client_name = client_obj.get_name()
    company_name = company[0]
    lower_limit = company[1]
    upper_limit = company[2]
    print(f"Verificando {company_name} para {client_name}")
    current_value = self._companies[company_name]["value"]      
    print(f"A acao da empresa {company_name} esta valendo {current_value}")
    print(f"Limites definidos por {client_name}: {lower_limit}, {upper_limit}")
    
    if current_value <= lower_limit or current_value >= upper_limit:  
      # Notifica cliente
      self.notify_client(client_obj, f"A acao da empresa {company_name} esta valendo {current_value}")

  def check_notify_requests(self):
    print("*"*40 + "\n" + "Verificando necessidade de notificacoes...")
    for client_name in self._clients:
      if "notify" in self._clients[client_name]: # Se o cliente tiver pedido notificao assincrona
        # Lista contendo tuplas (empresa, limite de perda, limite de ganho)
        client_notify = self._clients[client_name]["notify"] 
        # Lista contendo nomes das empresas que o cliente quer receber notificacoes
        client_companies = [c[0] for c in client_notify]
        # Lista contendo as empresas que tiveram seu valor alterado
        changed_companies = []
        print("\n")
        for company in self._companies:
          if self._companies[company]["changed"]:
            changed_companies.append(company)
            self._companies[company]["changed"] = False
            print(f"****Acao de {company} mudou seu valor****")
        print("\n")

        for c in client_notify:
          print(f"Empresa de interesse de {client_name}: {c[0]}")
          # Se uma das empresas que o cliente tem interesse em receber notificacoes mudou seu valor
          if c[0] in changed_companies:
            self.check_limits(self._clients[client_name]["reference"], c)

  def set_transaction(self, client_obj, option, stock, price, timeout):
    client_name = client_obj.get_name()
    transaction_type = "compra" if option == 1 else "venda"
    
    print(f"Recebeu pedido de {transaction_type} {client_name}")
    print_stock(stock)

    transaction = {
      "type": transaction_type,
      "stock": stock,
      "price": price,
      "timeout": timeout
    }

    if client_name in self._clients:
      if "transactions" in self._clients[client_name]:
        self._clients[client_name]["transactions"].append(transaction)
      else:
        self._clients[client_name]["transactions"] = []
        self._clients[client_name]["transactions"].append(transaction)
        if "reference" not in self._clients[client_name]:
          # Referencia ainda nao foi adicionada
          self._clients[client_name]["reference"] = client_obj
    else:
      self._clients[client_name] = {} 
      self._clients[client_name]["reference"] = client_obj 
      self._clients[client_name]["transactions"] = [] 
      self._clients[client_name]["transactions"].append(transaction)

  def register_notify(self, client_obj, company, lower_limit, upper_limit):
    client_name = client_obj.get_name()
    print(f"{client_name} registrou interesse em receber notificacoes assincronas sobre {company}")
    info = (company, lower_limit, upper_limit)
    # Cliente ja adicionado?
    if client_name in self._clients:
      # Ja pediu uma notificao antes?
      if "notify" in self._clients[client_name]:
        # Entao tem a estrutura completa, apenas adiciona a nova notificacao
        # Desse modo se um cliente pedir uma nova notificacao sobre a mesma empresa ela sera adicionada junto
        # Se uma mudanca do valor da acao estiver dentro do limite de ambas ele sera notificado duas vezes
        self._clients[client_name]["notify"].append(info)
      else: # Nunca pediu notificacao antes
        self._clients[client_name]["notify"] = [] # Inicializa uma lista vazia de notificacoes
        self._clients[client_name]["notify"].append(info)  # Adiciona nova notificacao
        if "reference" not in self._clients[client_name]:
          # Referencia ainda nao foi adicionada
          self._clients[client_name]["reference"] = client_obj 
    # Primeira interecao com o cliente
    else:
      self._clients[client_name] = {} # Inicializa um dict vazio para informacoes do client
      self._clients[client_name]["reference"] = client_obj # Referencia para objeto remoto (usado para chamar metodo notify_client)
      self._clients[client_name]["notify"] = [] # Inicializa uma lista vazia de notificacoes
      self._clients[client_name]["notify"].append(info) # Adiciona nova notificacao

  def register_interest(self, client_name, company):
    print(f"{client_name} registrou interesse em {company}")
    if client_name in self._clients:
      self._clients[client_name]["interests"].add(company)
    else:
      self._clients[client_name] = {} # Inicializa um dict vazio para informacoes do client
      self._clients[client_name]["interests"] = set()
      self._clients[client_name]["interests"].add(company)
    #print(self._clients[client_name]["interests"])

  def remove_interest(self, client_name, company):
    if client_name in self._clients:
      if company in self._clients[client_name]["interests"]:
        self._clients[client_name]["interests"].remove(company)
        print(f"{client_name} removeu interesse em {company}")
      else:
        print(f"{client_name} nao tinha interesse {company}, nada foi feito")
    else:
      print(f"{client_name} nao tinha nenhum interesse previo, nada foi feito")

  def get_interests_quotes(self, client_name):
    quotes = []
    if client_name in self._clients:
      for interest in self._clients[client_name]["interests"]:
        quote = (interest, self._companies[interest]["value"])
        quotes.append(quote)
    return quotes

  @Pyro4.oneway
  def notify_client(self, client_obj, message):
    print("Enviando notificacao para cliente")
    try:
      time.sleep(5)
      client_obj.notify(message)
    except Exception as e:
      print("Erro notify_client")
      print(e)
      exit()
    print("Cliente notificado\n\n")

  # Retorna uma quantidade aleatorio de algumas acoes possiveis
  # Essa implementacao simplifica a compra e venda de acoes, pois podemos supor que os clientes tem algumas acoes iniciais ja 
  def get_random_stocks(self):
    stocks = []
    for company in self._companies.keys():
      # Decide aleatoriamente se vai dar acoes de "company" para cliente
      if random.choice([True, False]):
        # Decide a quantidade
        quantity = random.randint(1, 20)
        stocks.append( new_stock(company, quantity) )
    return stocks

if __name__ == "__main__":
  c = StockMarketClient(0, "victor")
  companies = Company.getDefaultCompanies()
  print(c)
  [print(_) for _ in companies]
  time.sleep(10)
  [print(_) for _ in companies]