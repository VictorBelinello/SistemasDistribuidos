import threading
import sys
sys.path.append("core")

from core.market import StockMarket
from core.company import getDefaultCompanies

import Pyro5.server
import Pyro5.nameserver
import Pyro5.core


def start_nameserver():
    # Inicia uma thread para rodar o nameserver em localhost
    threading.Thread(target=Pyro5.nameserver.start_ns_loop, daemon=True).start()

if __name__ == "__main__":
    # Inicia o nameserver
    start_nameserver()

    print("Nameserver inicializado")
    # Instancia um stock market nomeado M01, usando um conjunto padrão de empresas 
    market_name = "M01"
    market = StockMarket(market_name, getDefaultCompanies())

    # Inicia um daemon
    with Pyro5.server.Daemon() as daemon:
        # Registra market no daemon, usando como nome market_name
        uri = daemon.register(market, market_name)
        print(f"URI de {market_name}: {uri}")

        # Localiza um nameserver
        nameserver = Pyro5.core.locate_ns()
        # Registra market com nome em market_name no nameserver
        nameserver.register(market_name, uri)
        # Inicia o requestLoop do daemon, continua no loop enquanto market._must_shutdown = False
        daemon.requestLoop(loopCondition=lambda : not market._must_shutdown)

    print("Servidor finalizando")
    
