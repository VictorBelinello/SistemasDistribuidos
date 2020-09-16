from stockmarket import StockMarket
from stock import Stock, StockTransaction
from subscription import Subscription

import random
import time
import os
os.environ["PYRO_LOGFILE"] = "pyro.log"
os.environ["PYRO_LOGLEVEL"] = "DEBUG"

from Pyro5.api import expose, Daemon, locate_ns, start_ns_loop, oneway
from Pyro5.errors import get_pyro_traceback
from threading import Thread, Lock

@expose
class StockServer(object):
    def __init__(self):
        self._markets = []
        self._interests = {}
        self._subscribers = {}
        self._references = {}
        self._transactions = {
            'buy': [],
            'sell': []
        }
        self._lock = Lock()
        
        Thread(target=self.update_all_quotes,daemon=True).start()
        Thread(target=self.update_transaction_timers,daemon=True).start()
        
    def add_stockmarket(self, stockmarket):
        with self._lock:
            self._markets.append(stockmarket)
    
    def get_quote(self, symbol):
        """Retorna a cotação atual do símbolo. Se não encontrar nenhum retorna None."""
        for market in self._markets:
            if market.has_symbol(symbol):
                quote = market.quotes[symbol]
                return quote
        return None

    def init_viewer(self, viewer_id, viewer):
        self._interests[viewer_id] = set()
        self._subscribers[viewer_id] = set()
        self._references[viewer_id] = viewer

    def remove_viewer(self, viewer_id):
        print(f"Removendo {viewer_id}")
        del self._interests[viewer_id]
        del self._subscribers[viewer_id]
        del self._references[viewer_id]

    def give_random_stocks(self):
        """Chamado inicialmente para dar algumas ações para viewer."""
        stocks = []
        number_of_stocks_per_market = 3
        for market in self._markets:
            market_stocks = market.random_stocks(number_of_stocks_per_market)  
            stocks += market_stocks
        return stocks

    def update_all_quotes(self):
        min_wait_time_seconds = 0
        wait_time_seconds = 2
        while True:
            for market in self._markets:
                market.update_quotes()
            self.check_all_subscriptions()
            time.sleep(min_wait_time_seconds + random.random() * wait_time_seconds)

    #############################################################################
    def add_viewer_interest(self, viewer_id, symbol):
        """Adiciona um interesse(símbolo) de viewer no servidor, se symbol estiver em algum dos mercados do servidor."""
        with self._lock:
            print(f"{symbol} adicionado como interesse de {viewer_id}.")
            self._interests[viewer_id].add(symbol)

    def remove_viewer_interest(self, viewer_id, symbol):
        """Remove um interesse(símbolo) de viewer do servidor, se existir, senão não faz nada."""
        with self._lock:
            print(f"{symbol} removido de interesses de {viewer_id}.")
            self._interests[viewer_id].remove(symbol)

    def get_viewer_interest_quotes(self, viewer_id):
        """Retorna uma lista com as cotações de interesse do viewer."""
        print(f"Lista de interesses de {viewer_id} enviada.")
        quotes = []
        for symbol in self._interests[viewer_id]:
            val = self.get_quote(symbol)
            if val is not None :
                quotes.append( (symbol, val) )
        return quotes
    
    #############################################################################
    def add_viewer_subscription(self, viewer_id, sub_tuple):
        """Adiciona uma inscrição de viewer no servidor"""
        sub = Subscription.from_tuple(sub_tuple)
        with self._lock:
            print(f"{viewer_id} inscrito em {sub}.")
            self._subscribers[viewer_id].add(sub)

    def should_notify(self, subscription):
        symbol = subscription._symbol 
        low = subscription._lower_limit
        high = subscription._upper_limit

        quote = self.get_quote(symbol)
        if quote:
            if quote <= low or quote >= high:
                return True
        return False

    @oneway
    def notify_viewer(self, viewer, message):
        # O método pode executar em uma thread diferente toda vez que for chamado
        # Por isso é necessário obter ownership
        viewer._pyroClaimOwnership()
        try:
            viewer.notify(message)
        except Exception as e:
            print("Falha na notificação do viewer")
            print("".join(get_pyro_traceback()))

    @oneway
    def notify_viewer_transaction(self, viewer, transaction):
        # O método pode executar em uma thread diferente toda vez que for chamado
        # Por isso é necessário obter ownership
        viewer._pyroClaimOwnership()
        try:
            viewer.notify_transaction(transaction)
        except Exception as e:
            print("Falha na notificação de transação do viewer")
            print("".join(get_pyro_traceback()))

    def check_all_subscriptions(self):
        """Verifica as inscrições para notificação assíncrona."""
        symbols_to_remove = set()
        for market in self._markets:
            for _id in self._subscribers:
                for evt in self._subscribers[_id]:
                    # market é um cópia, precisa do indice na lista também para acessar diretamente
                    if evt._symbol in market._quotes_changed: # Se o simbolo mudou
                        symbols_to_remove.add(evt._symbol)
                        val = market.quotes[evt._symbol]
                        if self.should_notify(evt):
                            ref = self._references[_id]
                            message = f"{evt._symbol} atingiu {val} fora de [{evt._lower_limit}, {evt._upper_limit}]"
                            self.notify_viewer(ref, message)
            # Remove o que for necessario
            for symb in symbols_to_remove:
                market._quotes_changed.remove(symb)
            # Reseta simbolos para remover
            symbols_to_remove = set()
    #############################################################################
    
    def add_viewer_transaction(self, viewer_id, transaction_dict):       
        transaction = StockTransaction.from_dict(transaction_dict)
        with self._lock:
            print(f"{viewer_id} transacionando {transaction}.")
            if transaction.is_selling:
                self._transactions['sell'].append( (viewer_id, transaction) )
            else:
                self._transactions['buy'].append( (viewer_id, transaction) )
            self.check_all_transactions()

    def check_all_transactions(self):
        for  sell_t in self._transactions['sell']:
            for  buy_t in self._transactions['buy']:
                # Verfica se pode transacionar ações
                if sell_t[1].can_trade(buy_t[1]):
                    seller, sell_transac = sell_t
                    self.notify_viewer_transaction(self._references[seller], vars(sell_transac))
                    buyer, buy_transac = buy_t
                    self.notify_viewer_transaction(self._references[buyer], vars(buy_transac))
                    # Remove as transações das listas
                    self._transactions['sell'].remove(sell_t)
                    self._transactions['buy'].remove(buy_t)

    def update_transaction_timers(self):
        # Para efeito de demonstração aqui a unidade de tempo minima é um segundo
        # Se TIME_UNITY_SECONDS fosse 60, a unidade de condition_timeout seria minutos e assim por diante
        TIME_UNITY_SECONDS = 1
        while True:
            for t in self._transactions['sell']:
                transaction = t[1]
                # Atualiza os timers, retorna o novo valor
                if transaction.update_timeout() == 0:
                    # Se acabou o timer retira transação
                    self._transactions['sell'].remove(t)
            for t in self._transactions['buy']:
                transaction = t[1]
                # Atualiza os timers, retorna o novo valor
                if transaction.update_timeout() == 0:
                    # Se acabou o timer retira transação
                    self._transactions['buy'].remove(t)
            time.sleep(TIME_UNITY_SECONDS)

if __name__ == "__main__":
    # Inicia uma thread para rodar o nameserver em localhost
    Thread(target=start_ns_loop, daemon=True).start()

    nasdaq = StockMarket("NASDAQ",  ["AAPL", "INTC", "NVDA", "QCOM", "CSCO", "TSLA", "TSM", "MSFT", "GOOG"] )
    serv = StockServer()
    serv.add_stockmarket(nasdaq)
    with Daemon() as daemon:
        # Registra o objeto no daemon
        #daemon.register(Stock)
        server_uri = daemon.register(serv)
        # Localiza o nameserver
        with locate_ns() as ns:
            # Registra o objeto no nameserver usando o nome stockmarket.server
            ns.register("stockmarket.server", server_uri)
        print("Servidor do mercado de ações pronto.")
        daemon.requestLoop()