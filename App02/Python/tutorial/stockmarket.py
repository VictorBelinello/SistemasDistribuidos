import random
import time
import Pyro4
import os
from threading import Thread

@Pyro4.expose
class StockMarket():
  def __init__(self, companies):
    # companies eh uma lista contendo nomes das empresas no mercado
    self._companies = {}
    for company in companies:
      self._companies[company] = round( random.uniform(5, 200), 2 ) # Inicia com valor aleatoio
    # Dicionario contendo todas as informacoes relevantes dos clientes
    # Tera uma entrada para cada cliente, onde o nome dele eh a chave (nao eh unico, mas para simplificar a aplicacao sera assim)
    # self.clients["victor"] tera as informacoes do cliente "victor" guardadas tambem em forma de dicionario
    # self.clientes["victor"]["interests"] eh um set (lista sem repeticoes) contendo as empresas que o cliente "victor" esta interessado
    self._clients = {}

  def generate_quotes(self):
    while True: # Loop infito simulando variacoes de quotacoes
      # Percorre todas as empresas 
      for company in self._companies.keys():
        # Decide aleatoriamente se vai alterar o valor da acao da empresa
        if random.choice([True, False]):
          # Gera um valor aleatorio para acao entre 5 e 200 arredondado para 2 casas
          self._companies[company] = round( random.uniform(5, 200), 2 ) 
      # Espera um tempo aleatorio para continuar
      time.sleep( random.random() ) 

  @property
  def companies(self):
    return self._companies

  def register_interest(self, client, company):
    print(f"{client} registrou interesse em {company}")
    if client in self._clients:
      self._clients[client]["interests"].add(company)
    else:
      self._clients[client] = {} # Inicializa um dict vazio
      self._clients[client]["interests"] = set()
      self._clients[client]["interests"].add(company)

  def remove_interest(self, client, company):
    if client in self._clients:
      if company in self._clients[client]["interests"]:
        self._clients[client]["interests"].remove(company)
        print(f"{client} removeu interesse em {company}")
      else:
        print(f"{client} nao tinha interesse {company}, nada foi feito")
    else:
      print(f"{client} nao tinha nenhum interesse previo, nada foi feito")

  def get_interests_quotes(self, client):
    quotes = {}
    if client in self._clients:
      for interest in self._clients[client]["interests"]:
        quotes[interest] = self._companies[interest]
    return quotes

  @Pyro4.oneway
  def notify_client(self, obj):
    try:
      time.sleep(5)
      obj.notify()
    except Exception as e:
      print("Erro notify_client")
      print(e)
      exit()
    print("Client notified")

def startNameServer():
    os.system("python -m Pyro4.naming")

if __name__ == "__main__":
  # Cria uma nova thread para rodar o servidor de nomes
  Thread(target=startNameServer, daemon=True).start()

  # Essa lista contem todas as empresas disponiveis na aplicacao
  companies = ["AAPL", "CSCO", "MSFT", "GOOG", "IBM", "HPQ", "BP"]
  sm = StockMarket(companies)

  # Registra classe com um Pyro4.daemon
  daemon = Pyro4.Daemon()
  uri = daemon.register(sm)

  # Adiciona o daemon (identificado por uri) no name server
  name_server = Pyro4.locateNS()
  name_server.register("stockmarket", uri)
  
  Thread(target=sm.generate_quotes, daemon=True).start()

  print("Client can start")

  # Inicia o loop do daemon para verificar chamadas remotas
  daemon.requestLoop()
