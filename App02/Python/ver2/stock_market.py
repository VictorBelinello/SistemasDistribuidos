from stock_market_company import Company
import Pyro4
import sys
sys.path.append(".")


@Pyro4.expose
class StockMarket(object):
    def __init__(self, companies=Company.getDefaultCompanies()):
        # Lista de objetos Company.
        self._companies = companies
        # Dicionario de objetos StockMarketClient.
        self._clients = {}

    def addClient(self, client):
        """Esse método é chamado pelo cliente em linkStockMarket."""
        print("Cliente {0} adicionado na lista.".format(client.id))
        # Adiciona novo cliente no dicionário usando o id como chave
        self._clients[client.id] = client
        print(client.name)
        print(client.quotes)

    def getQuotes(self, client_id):
        """Obtém a lista cotações do cliente especificado."""
        print("Cliente {0} pediu a lista cotações.".format(client_id))
        client = self._clients[client_id]
        return client.quotes

    def addQuote(self, client_id, company):
        """Adiciona a empresa na lista cotações do cliente."""
        print("Cliente {0} pediu para adicionar {1} na lista.".format(
            client_id, company.name))
        client = self._clients[client_id]
        client.appendQuote(company)

    def removeQuote(self, client_id, company):
        """Remove a empresa da lista cotações do cliente."""
        print("Cliente {0} pediu para remover {1} da lista.".format(
            client_id, company.name))
        client = self._clients[client_id]
        client.deleteQuote(company)

    def getSubscriptions(self, client_id):
        """Obtém a lista cotações do cliente especificado."""
        print("Cliente {0} pediu a lista de eventos inscritos.".format(client_id))
        client = self._clients[client_id]
        return client.subscriptions

    def addSubscription(self, client_id, subscription):
        """Adiciona a empresa na lista cotações do cliente."""
        print("Cliente {0} se inscreveu em evento sobre {1} na lista.".format(
            client_id, subscription.company.name))
        client = self._clients[client_id]
        client.appendSubscription(company)

    def removeSubscription(self, client_id, subscription):
        """Remove a empresa da lista cotações do cliente."""
        print("Cliente {0} removeu inscrição em evento sobre {1} da lista.".format(
            client_id, subscription.company.name))
        client = self._clients[client_id]
        client.deleteSubscription(subscription)

    @Pyro4.oneway
    def notifyClient(self, client):
        """Método usado para notificar o cliente.
        Internamente chama o método notify fornecido pelo cliente"""
        try:
            client.notify()
        except Exception as e:
            print("Erro notifyClient")
            print(e)
            exit()

    @property
    def companies(self):
        return self._companies


if __name__ == "__main__":
    sm = StockMarket()
    print(sm.companies)
