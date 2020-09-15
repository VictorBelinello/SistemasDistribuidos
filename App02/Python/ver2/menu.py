import os
from stock_market_utils import Subscription

class Menu:
    """Classe para apresentar o menu da aplicação.
    Construtor recebe como único parâmetro um objeto do tipo StockMarketClient representando o cliente dono do menu."""
    # String usada para finalizar/separar um menu, para melhor visualização
    SEPARATOR = "*"*30
    HEADLINE_WIDTH = 30

    def __init__(self, master):
        self.master = master

    @staticmethod
    def getNumericInput(cast=int, input_message="Opção: "):
        """Obtém uma opção de menu do usuário e converte de acordo com o argumento cast."""
        opt = input(input_message)
        try:
            opt = cast(opt)
            return opt
        except ValueError as e:
            print("Erro convertendo '{0}' para {1}".format(opt, cast))
            input("Pressione ENTER.")
        finally:
            # Limpa o terminal de acordo com o SO
            os.system('cls' if os.name == 'nt' else 'clear')

    def getCompanyInput(self):
        """Procura uma empresa pelo nome fornecido pelo usuário e retorna o objeto Company equivalente, se não encontrar retorna None"""
        company_name = input("Informe nome da empresa: ").upper()
        companies = self.master.getAllCompanies()
        for company in companies:
            if company.name == company_name:
                return company
        # Não encontrou a empresa desejada
        print("Empresa não encontrada {0}.\nAqui estão as empresas cadastradas:\n{1}".format(
            company_name, self.master.getAllCompanyNames()))
        return None

    def getSubscriptionInput(self):
        company = self.getCompanyInput()
        if not company:
            return None
        print("O evento pode ser relacionado a um limite\nde ganho(notifica quando passa do valor) ou\nde perda(notifica quando fica abaixo do valor)")
        print("Digite 1 para limite de ganho e 2 para limite de perda")
        limit_type = self.getNumericInput()
        if limit_type != Subscription.UPPER_LIMIT and limit_type != Subscription.LOWER_LIMIT:
            print("O valor deve ser {0} ou {1}".format(Subscription.UPPER_LIMIT, Subscription.LOWER_LIMIT))
            return None
        price_trigger = self.getNumericInput(cast=float, input_message="Digite o preço limite: ")
        return Subscription(company, limit_type, price_trigger)

    def optionQuotes(self, redirect=False):
        """Apresenta o menu COTAÇÕES"""
        print("MENU COTAÇÕES".center(Menu.HEADLINE_WIDTH))
        print("Digite 1 para mostrar sua lista cotações")
        print("Digite 2 para adicionar uma empresa")
        print("Digite 3 para remover uma empresa")
        print("Digite 0 para voltar ao menu principal")
        print(Menu.SEPARATOR)

        opt = Menu.getNumericInput()

        if opt == 1:
            quotes = self.master.getQuotes()
            string = "Lista cotações vazia." if not quotes else "".join(
                map(str, quotes))
            print(string)
            print(Menu.SEPARATOR)
            input("ENTER para prosseguir.")
        elif opt == 2 or opt == 3:
            company = self.getCompanyInput()
            if company and opt == 2:
                self.master.addQuote(company)
            elif company and opt == 3:
                self.master.removeQuote(company)
            print(Menu.SEPARATOR)
            input("ENTER para prosseguir.")

    def optionStocks(self):
        """Apresenta o menu AÇÕES"""
        print("MENU AÇÕES".center(Menu.HEADLINE_WIDTH))
        print("Digite 1 para mostrar suas ações")
        print("Digite 2 para comprar uma ação")
        print("Digite 3 para vender uma ação")
        print("Digite 0 para voltar ao menu principal")
        print(Menu.SEPARATOR)

        opt = Menu.getNumericInput()

        if opt == 1:
            print("NOT IMPLEMENTED YET")
            raise NotImplementedError
        elif opt == 2 or opt == 3:
            company = self.getCompanyInput()
            if company:
                pass
            print(Menu.SEPARATOR)
            input("ENTER para prosseguir.")

    def optionSubscriptions(self):
        """Apresenta o menu INSCRIÇÕES"""
        print("MENU INSCRIÇÕES".center(Menu.HEADLINE_WIDTH))
        print("Digite 1 para ver eventos inscritos")
        print("Digite 2 para se inscrever em um novo evento")
        print("Digite 0 para voltar ao menu principal")
        print(Menu.SEPARATOR)

        opt = Menu.getNumericInput()

        if opt == 1:
            subscriptions = self.master.getSubscriptions()
            string = "Lista eventos vazia." if not subscriptions else "".join(
                map(str, subscriptions))
            print(string)
            print(Menu.SEPARATOR)
            input("ENTER para prosseguir.")
        elif opt == 2:
            subscription = self.getSubscriptionInput()
            if subscription:
                print(subscription)
            print(Menu.SEPARATOR)
            input("ENTER para prosseguir.")

    def showMainMenu(self):
        """Apresenta o menu PRINCIPAL"""
        while True:
            # Limpa o terminal de acordo com o SO
            os.system('cls' if os.name == 'nt' else 'clear')
            print("MENU PRINCIPAL".center(Menu.HEADLINE_WIDTH))
            print("Digite 1 para gerir lista cotações")
            print("Digite 2 para gerir suas ações")
            print("Digite 3 para gerir alertas")
            print("Digite 0 para sair")
            print(Menu.SEPARATOR)

            opt = Menu.getNumericInput()

            if opt == 1:
                self.optionQuotes()
            elif opt == 2:
                self.optionStocks()
            elif opt == 3:
                self.optionSubscriptions()
            elif opt == 0:
                break
