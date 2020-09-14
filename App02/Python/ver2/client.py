import sys
sys.path.append(".")
from stock_market_client import StockMarketClient
from stock_market_company import Company
from menu import Menu

import Pyro4
from threading import Thread

if __name__ == "__main__":
   # clientTest(StockMarketClient("Teste"))

    print("Obtendo referencia para objeto remoto...")
    name_server = Pyro4.locateNS()
    uri = name_server.lookup("stockmarket")
    sm = Pyro4.Proxy(uri) # O Pyro4.Proxy ira agir como se fosse o objeto desejado
    print("Referencia obtida!\n")

    name = input("Informe seu nome: ")
    client = StockMarketClient(name)    
    # Configurando cliente para receber callback do servidor (notify)
    daemon = Pyro4.Daemon()
    uri = daemon.register(client)

    Thread(target=daemon.requestLoop, daemon=True).start()

    client.linkStockMarket(sm)
    m = Menu(client)
    m.showMainMenu()
    print("\nSaindo do menu\n")
    client.getAllCompanies()
    input()