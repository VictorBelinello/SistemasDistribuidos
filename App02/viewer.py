import os

from stock import Stock, StockTransaction
from subscription import Subscription

from Pyro5.api import expose, callback


class Viewer(object):
    def __init__(self):
        self._id = id(self)
        self._server = None
        self._stocks = []

    @property
    def id(self):
        return self._id
        
    @expose
    @callback
    def notify(self, message):
        print(f"Notificação do servidor: {message}")
    
    @expose
    @callback
    def notify_transaction(self, transaction):
        t = StockTransaction.from_dict(transaction)
        print(f"Notificação de transação: {t}")
        if t.is_selling :
            # Pega a ação equivalente na lista stocks
            owned_stock = [s for s in self._stocks if s.symbol == t.symbol][0]
            owned_stock.remove_amount(t.amount)
            if owned_stock.amount == 0:
                self._stocks.remove(owned_stock)
        else:
            # Pega a ação equivalente na lista stocks, não acessa imediatamente pois pode ser uma ação nova que foi adquirida
            owned_stock = [s for s in self._stocks if s.symbol == t.symbol]
            if owned_stock == []:
                # Ação nova
                self._stocks.append(Stock(t.symbol, t.amount))
            else:
                owned_stock[0].add_amount(t.amount)


    def attach_to_server(self, server):
        self._server = server
        server.init_viewer(self.id, self)
        # Aproveita que agora tem um servidor e pega alguma ações iniciais
        stocks = self._server.give_random_stocks()
        for s in stocks:
            val = Stock.from_dict(s)
            self._stocks.append(val)

    def dettach_from_server(self):
        self._server.remove_viewer(self.id)

    def add_interest(self):
        symbol = input("Informe nome do símbolo: ").upper()
        if self._server:
            self._server.add_viewer_interest(self.id, symbol)

    def remove_interest(self):
        symbol = input("Informe nome do símbolo: ").upper()
        if self._server:
            self._server.remove_viewer_interest(self.id, symbol)

    def list_interest(self):
        if self._server:
            quotes = self._server.get_viewer_interest_quotes(self.id)
            print(quotes)

    def list_all_symbols(self):
        if self._server:
            symbols = self._server.get_all_symbols()
            print(symbols)

    def list_stocks(self):
        for s in self._stocks:
            print(s)

    def add_subscription(self):
        if self._server:
            sub = Subscription.get_from_user()
            self._server.add_viewer_subscription(self.id, sub)

    def add_transaction(self):
        if self._server:
            transaction = StockTransaction.get_from_user(self._stocks)
            if transaction:
                self._server.add_viewer_transaction(self.id, transaction)

    def show_menu(self):
        menu = {
        0: self.dettach_from_server,
        1: self.list_interest,
        2: self.add_interest,
        3: self.remove_interest,
        4: self.add_subscription,
        5: self.list_stocks,
        6: self.add_transaction,
        7: self.list_all_symbols,
        }
        opt = -1
        while opt != 0:
            # Limpa o terminal de acordo com o SO
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Digite 1 para listar cotações")
            print("Digite 2 para inserir em sua lista cotações")
            print("Digite 3 para remover de sua lista cotações")
            print("Digite 4 para adicionar inscrição para evento")
            print("Digite 5 para listar ações")
            print("Digite 6 para comprar/vender ações")
            print("Digite 7 para listar todos os símbolos")
            print("Digite 0 para sair")
            print("*"*30)

            try:
                opt = int(input("Opção: "))
                if opt > 7 or opt < 0:
                    raise ValueError
                func = menu[opt]
                func()
            except ValueError:
                print("Opção inválida")
            finally:
                input("ENTER para continuar...")