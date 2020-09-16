from Pyro5.api import Proxy
from Pyro5.server import Daemon
from Pyro5.errors import NamingError, get_pyro_traceback

from viewer import Viewer
from stock import Stock, StockTransaction
from threading import Thread

def find_stockmarket_server():
    try:
        server = Proxy("PYRONAME:stockmarket.server")
    except Exception as e:
        print("Problema conectando com servidor.")
        print(e)

def main():
    print("Obtendo referência para servidor.")
    # Usa o meta-protocolo do Pyro, permite um sintaxe simplificada para obter o nameserver e realizar a buscar pelo objeto
    # https://pyro5.readthedocs.io/en/latest/nameserver.html#nameserver-pyroname
    uri = "PYRONAME:stockmarket.server"
    with Proxy(uri) as server:
        try:
            server._pyroBind()
        except NamingError as e:
            print(f"Houve um problema ao tentar encontrar stockmarket.server. O servidor está rodando?")
            exit() 

        print("Referência para servidor obtida.")
        viewer = Viewer()
        with Daemon() as daemon:
            try:
                daemon.register(viewer)
                Thread(target=daemon.requestLoop, daemon=True).start()
                
                viewer.attach_to_server(server)
                input("ENTER para ir para menu...")
                
                viewer.show_menu()
            except NamingError as e:
                print(e)
                print("".join(get_pyro_traceback()))

if __name__ == "__main__":
    main()