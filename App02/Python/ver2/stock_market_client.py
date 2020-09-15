import Pyro4
from stock_market_utils import Subscription

class StockMarketClient(object):
    def __init__(self, name):
        # Identificador único do cliente
        self._id = id(self)
        # Nome do cliente.
        self._name = name
        # Lista de ações de interesse do cliente. Os elementos são do tipo Company.
        # Localmente a lista sempre está vazia, deve ser chamado o método getQuotes de market para obter a lista atualizada
        self._quotes = []
        # Lista de ações sobre as quais o cliente deseja ser notificado de modo assíncrono.
        # Mesmo comportamente de self._quotes
        self._subscriptions = []
        # Referência para objeto remoto StockMarket. Preenchida através do método linkStockMarket.
        self.market = None

    @Pyro4.expose
    @Pyro4.callback
    def notify(self, message):
        """Método do cliente, chamado pelo servidor para notificar sobre algum evento."""
        print("Notificação do servidor: {}".format(message))

    @Pyro4.expose
    @property
    def id(self):
        return self._id

    @Pyro4.expose
    @property
    def name(self):
        return self._name

    # O atributo _quotes não está exposto. Logo são necessárias funções para manipular ele
    @Pyro4.expose
    @property
    def quotes(self):
        return self._quotes

    @Pyro4.expose
    def appendQuote(self, quote):
        """Método chamado pelo servidor para adicionar uma empresa na lista cotações."""
        self._quotes.append(quote)

    @Pyro4.expose
    def deleteQuote(self, quote):
        """Método usado pelo servidor para remover uma empresa da lista cotações."""
        try:
            self._quotes.remove(quote)
        except Exception as e:
            print("{} não estava na lista, nada foi feito.".format(quote.name))

    # O atributo _subscriptions não está exposto. Logo são necessárias funções para manipular ele
    @Pyro4.expose
    @property
    def subscriptions(self):
        return self._subscriptions

    @Pyro4.expose
    def appendSubscription(self, subscription):
        """Método chamado pelo servidor para adicionar uma empresa na lista cotações."""
        self._subscriptions.append(subscription)

    @Pyro4.expose
    def deleteSubscription(self, subscription):
        """Método usado pelo servidor para remover uma empresa da lista cotações."""
        try:
            self._subscriptions.remove(subscription)
        except Exception as e:
            print("{} não estava na lista, nada foi feito.".format(subscription.name))

    def __str__(self):
        return "{}".format(self._name)

    def __repr__(self):
        return str(self)

    def getQuotes(self):
        """Retorna uma lista de tuplas contendo as empresas e respectivos valores das ações."""
        # Obtem a lista cotações contendo objetos Company
        quotes = self.market.getQuotes(self.id)
        return [(company.name, company.stock_value) for company in quotes]

    def addQuote(self, company):
        """Adiciona uma empresa na lista cotações, se ela ainda não estiver na lista"""
        if company in self.quotes:
            return
        self.market.addQuote(self.id, company)

    def removeQuote(self, company):
        """Remove uma empresa na lista cotações, se ela estiver na lista"""
        if company in self.market.getQuotes(self.id):
            self.market.removeQuote(self.id, company)
        else:
            print("Item não existia, sem alterações.")

    def getSubscriptions(self):
      """Retorna uma lista de tuplas contendo informações do evento inscrito."""
      # Obtem a lista de eventos contendo objetos Subscription
      subscriptions = self.market.getSubscriptions(self.id)
      return [(event.company, event.trigger) for event in subscriptions]

    def linkStockMarket(self, market):
        """Método usado para linkar o cliente específico com o objeto StockMarket, adicionando o mesmo na lista de clientes de market."""
        self.market = market
        self.market.addClient(self)

    def getAllCompanies(self):
        return self.market.companies

    def getAllCompanyNames(self):
        return [company.name for company in self.market.companies]


if __name__ == "__main__":
    c = StockMarketClient("victor")
    print(c)
    print(c.id)
