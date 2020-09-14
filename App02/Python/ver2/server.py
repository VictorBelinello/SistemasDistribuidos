import sys
sys.path.append(".")
from stock_market import StockMarket
from threading import Thread
import os
import Pyro4

def start_name_server():
    os.system("python -m Pyro4.naming")

if __name__ == "__main__":
  # Cria uma nova thread para rodar o servidor de nomes
  Thread(target=start_name_server, daemon=True).start()
  # Cria a bolsa de valores com empresas padrão (referenciadas em stock_market.py e definidas em stock_market_company.py)
  sm = StockMarket()

  # Registra classe com um Pyro4.daemon
  with Pyro4.Daemon() as daemon:
    uri = daemon.register(sm)
    print("Daemon registrado")
    with Pyro4.locateNS() as name_server:
      # Adiciona o daemon (identificado por uri) no name server
      name_server.register("stockmarket", uri)
      print("Aplicacao registrada no servidor de nomes")
    print("Inicializacao servidor concluida")
    print("*"*30)
    print("\n")
    # Inicia o loop do daemon para verificar chamadas remotas
    daemon.requestLoop()
