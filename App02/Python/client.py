import Pyro4
from threading import Thread
import sys
import os

from stock import print_stock, new_stock

class Client:
    def __init__(self, name, stock_market):
        self.name = name
        self.sm = stock_market
        # Obtem algumas acoes do mercado, para poder realizar vendas e compras
        self.stocks = self.sm.get_random_stocks()
        
    def set_transaction(self, option):
        if option == 1 or option == 2:
            company = self._get_company_input()
            quantity = input("Informe a quantidade(inteiro)\n")
            price = input("Informe o preco(maximo na compra ou minimo na venda), use . para separar casas decimais\n")
            timeout = input("Tempo para ficar em estado condicional(segundos)\n")
            try:
                quantity = int(quantity)
                price = float(price)
                timeout = float(timeout)
                s = new_stock(company, quantity)
                self.sm.set_transaction(self, option, s, price, timeout)
            except ValueError as e:
                input("Opcao invalida. Pressione ENTER para voltar ao menu")
                self.do_option(7)
        else:
            self.show_menu()

    @Pyro4.expose
    @Pyro4.callback
    def notify(self, message):
        print("\nNotificacao do servidor:\n")
        print(message)
        print("\n")
        
    @Pyro4.expose
    def get_name(self):
        return self.name

    def set_interest(self, company):
        self.sm.register_interest(self.name, company)

    def set_notify(self, company, lower_limit, upper_limit):
        print(f"Voce recebera notificacoes quando atingir um dos limites : [{lower_limit}, {upper_limit}]")
        sm.register_notify(self, company, lower_limit, upper_limit)
        #sm.notify_client(client)

    def list_companies(self, companies):
        print("Lista das empresas e o valor das acoes no mercado: ")
        res = list(zip(*companies))
        for name, value in companies:
            print(f"{name:<5}: {value}")
        print("\n")

    # Funcao auxiliar para do_option
    def _get_company_input(self):
        company = input("Informe o nome da empresa desejada.\n")
        company = company.upper() # Os nomes sao armazenados em letras maisculas
        # self.sm.companies retorna uma lista de tuplas com o nome e valor, mas so interessa o nome agora
        # monta uma lista com nomes de empresas extraindo o primeiro elemento da tupla para cada tupla na lista
        companies_available = [ c[0] for c in self.sm.companies]
        if company not in companies_available:
            input("Empresa invalida, pressione ENTER para voltar ao menu. Liste as empresas disponiveis no menu usando a opcao 1")
            self.show_menu()
        else:
            return company

    def do_option(self, option):
        if option == 1:
            self.list_companies(self.sm.companies)
        elif option == 2:
            company = self._get_company_input()
            self.sm.register_interest(self.name, company)
        elif option == 3:
            company = self._get_company_input()
            self.sm.remove_interest(self.name, company)
        elif option == 4:
            quotes = self.sm.get_interests_quotes(self.name)
            if not quotes:
                print("Nenhum interesse registrado no servidor")
            else:
                self.list_companies(quotes)
        elif option == 5:
            company = self._get_company_input()
            lower_limit = input("Informe o limite de perda, use . para separar casas decimais\n")
            lower_limit = round(float(lower_limit), 2)
            upper_limit = input("Informe o limite de ganho, use . para separar casas decimais\n")
            upper_limit = round(float(upper_limit), 2)
            self.set_notify(company, lower_limit, upper_limit)
        elif option == 6:
            print("Lista de acoes na carteira: ")
            print_stock(self.stocks)
        elif option == 7:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Digite 1 para compra")
            print("Digite 2 para venda")
            print("Digite 3 para voltar ao menu")
            opt = input("Opcao: ")
            try:
                opt = int(opt)
                self.set_transaction(opt)
            except ValueError as e:
                input("Opcao invalida. Pressione ENTER para voltar ao menu")
                self.do_option(7)
        elif option == 8:
            sys.exit()

        input("Pressione ENTER para continuar")
        
        self.show_menu()

    def show_menu(self):
        # Limpa o terminal de acordo com o SO
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Digite 1 para listar as empresas disponiveis")
        print("Digite 2 para inserir uma empresa na lista de interesse")
        print("Digite 3 para remover uma empresa na lista de interesse")
        print("Digite 4 para obter as cotacoes da sua lista de interesse")
        print("Digite 5 para inserir notificacao assincrona")
        print("Digite 6 para listar suas acoes")
        print("Digite 7 para realizar compra/venda")
        print("Digite 8 para sair do programa")
        print("*"*30)
        opt = input("Opcao: ")
        try:
            opt = int(opt)
            self.do_option(opt)
        except ValueError as e:
            input("Opcao invalida. Pressione ENTER para voltar ao menu")
            self.show_menu()
        print("*"*30)

if __name__ == "__main__":
    print("Obtendo referencia para objeto remoto...")
    name_server = Pyro4.locateNS()
    uri = name_server.lookup("stockmarket")
    sm = Pyro4.Proxy(uri) # O Pyro4.Proxy ira agir como se fosse o objeto desejado
    print("Referencia obtida!\n")

    name = input("Informe seu nome: ")
    client = Client(name, sm)    

    print("Inicializando callback")
    daemon = Pyro4.Daemon()
    daemon.register(client)

    
    Thread(target=daemon.requestLoop, daemon=True).start()

    client.show_menu()
        