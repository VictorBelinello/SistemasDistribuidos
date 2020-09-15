from threading import Thread
import Pyro4
from menu import Menu
from stock_market_company import Company
from stock_market_client import StockMarketClient
import sys
sys.path.append(".")


if __name__ == "__main__":
   # clientTest(StockMarketClient("Teste"))

    print("Obtendo referencia para objeto remoto...")
    name_server = Pyro4.locateNS()
    uri = name_server.lookup("stockmarket")
    # O Pyro4.Proxy ira agir como se fosse o objeto desejado
    sm = Pyro4.Proxy(uri)
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
