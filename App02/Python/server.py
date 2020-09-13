from stockmarket import StockMarket
from threading import Thread
import os
import Pyro4

def start_name_server():
    os.system("python -m Pyro4.naming")

if __name__ == "__main__":
  # Cria uma nova thread para rodar o servidor de nomes
  Thread(target=start_name_server, daemon=True).start()

  # Essa lista contem todas as empresas disponiveis na aplicacao
  companies = ["AAPL", "CSCO", "MSFT", "GOOG", "IBM", "HPQ", "BP"]
  sm = StockMarket(companies)

  # Registra classe com um Pyro4.daemon
  daemon = Pyro4.Daemon()
  uri = daemon.register(sm)
  print("Daemon registrado")

  # Adiciona o daemon (identificado por uri) no name server
  name_server = Pyro4.locateNS()
  name_server.register("stockmarket", uri)
  print("Aplicacao registrada no servidor de nomes")

  # Cria uma nova thread para gerar as alteracoes de cotacoes
  Thread(target=sm.generate_quotes, daemon=True).start()

  print("Inicializacao servidor concluida")
  print("*"*30)
  print("\n")
  # Inicia o loop do daemon para verificar chamadas remotas
  daemon.requestLoop()
