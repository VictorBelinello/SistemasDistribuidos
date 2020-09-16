import random
import time

from stock import Stock, StockTransaction

class StockMarket():
    def __init__(self, marketname, symbols):
        self._id = id(self)
        
        self._marketname = marketname
        
        self._quotes = {}
        for symbol in symbols:
            self._quotes[symbol] = round( random.uniform(5, 150), 2)
        
        self._quotes_changed = set()

        self._symbols = symbols
        
        self._transactions = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @property
    def quotes(self):
        return self._quotes

    @property
    def symbols(self):
        return self._symbols

    @property
    def name(self):
        return self._marketname      

    def update_quotes(self):
        # Escolhe um simbolo
        symbol = random.choice(self.symbols)
        # Escolhe um valor entre 5 e 150
        val = round( random.uniform(5, 150), 2)
        # Atribui o valor para o simbolo escolhido
        self._quotes[symbol] = val
        self._quotes_changed.add(symbol)

    def has_symbol(self, symbol):
        return symbol in self.symbols

    def random_stocks(self, number):
        """Chamado inicialmente para dar algumas ações para viewer."""
        return Stock.random(self.symbols, number) 


if __name__ == "__main__":
    nasdaq = StockMarket("NASDAQ",  ["AAPL", "INTC", "NVDA", "QCOM", "CSCO", "TSLA", "TSM", "MSFT", "GOOG"] )
    stocks = nasdaq.random_stocks(4)
    transactions = []
    for stock in stocks:
        s = StockTransaction(stock, False, 100, 5)
        transactions.append(s)
    print(stocks)
    print(transactions)