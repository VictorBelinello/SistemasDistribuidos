import sys
sys.path.append("core")
import threading

import Pyro5.api
import Pyro5.errors
import Pyro5.server

from stock_client import StockClient

if __name__ == "__main__":
    # Qual o mercado que o cliente desejaria "associar-se", na aplicação só existe um
    market_name = "M01"
    print("Obtendo referencia para objeto remoto...")
    # Obtém o servidor de nomes
    #name_server = Pyro5.api.locate_ns()

    # Encontra a locaçalização do objeto identificado por
    #uri = name_server.lookup("stockmarket")

    # A linha abaixo tem o mesmo resultado que as duas acima
    # https://pyro5.readthedocs.io/en/latest/nameserver.html#nameserver-pyroname
    uri = f"PYRONAME:{market_name}"
    
    with Pyro5.api.Proxy(uri) as market:
        try:
            market._pyroBind()
        except Pyro5.errors.NamingError as e:
            print(f"Houve um problema ao tentar encontrar {market_name}. O servidor está rodando?")
            print("".join(Pyro5.errors.get_pyro_traceback()))
            exit()    

        print("Referência obtida ")
        client = StockClient("victor")
        
        try:
            with Pyro5.server.Daemon() as daemon:
                daemon.register(client, client._name)
                threading.Thread(target=daemon.requestLoop, daemon=True).start()
                try:
                    client.addStockMarket(market)
                    input("Pressione ENTER para continuar...")
                    client.showMenu()
                except Exception:
                    print("Problema conectando StockMarket e Client")
                    print("".join(Pyro5.errors.get_pyro_traceback()))
        except Exception as e:
            print("Problema registrando cliente no daemon")
            print("".join(Pyro5.errors.get_pyro_traceback()))
            exit()
        finally:
            market.shutdown()