import Pyro4
from threading import Thread
import sys
import os


class Client:
    def __init__(self, name, stock_market):
        self.name = name
        self.sm = stock_market

    def set_interest(self, companies):
        self.sm.register_interest(self.name, companies)

    def list_companies(self, companies_dict):
        print("Lista das empresas e o valor das acoes no mercado")
        for k in companies_dict.keys():
            print(f"{k:<5}: {companies_dict[k]}")

    # Funcao auxiliar para do_option
    def _get_company_input(self):
        company = input("Informe o nome da empresa desejada.\n")
        company = company.upper() # Os nomes sao armazenados em letras maisculas
        if company not in self.sm.companies.keys():
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
            if quotes == {}:
                print("Nenhum interesse registrado no servidor")
            else:
                self.list_companies(quotes)
        elif option == 6:
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
        print("Digite 6 para sair do programa")
        print("*"*30)
        opt = input("Opção: ")
        self.do_option(int(opt))
        print("*"*30)

if __name__ == "__main__":
    print("Obtendo referencia para objeto remoto...")
    name_server = Pyro4.locateNS()
    uri = name_server.lookup("stockmarket")
    sm = Pyro4.Proxy(uri) # O Pyro4.Proxy ira agir como se fosse o objeto desejado
    print("Referencia obtida!\n")

    name = input("Informe seu nome: ")
    client = Client(name, sm)    
    client.show_menu()
    

    