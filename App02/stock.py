import random
from Pyro5.api import expose

class Stock(object):
    def __init__(self, symbol, amount):
        self._symbol = symbol
        self._amount = amount

    @property
    def symbol(self):
        return self._symbol
    
    @property
    def amount(self):
        return self._amount
    
    def __str__(self):
        return f"{self.amount} ações de {self.symbol}"
    def __repr__(self):
        return f"<STOCK>({self.symbol}:{self.amount})"

    def __eq__(self, other):
        return (self.symbol == other.symbol) and (self.amount == other.amount)

    @staticmethod
    def random(symbols, number):
        """Retorna o número especificado de ações aleatórias para o mercado especificado."""
        # Escolhe number símbolos sem repetição
        symbols = random.sample( symbols, k = number)
        # Entre 1 e 10 ações
        amounts = random.choices( range(1, 11) , k = number)
        stocks = []
        for item in zip(symbols, amounts):
            s = Stock(item[0], item[1])
            stocks.append( vars(s) )
        return stocks
    
    @staticmethod
    def from_dict(data):
        symbol = data.get('_symbol')
        amount = data.get('_amount')
        return Stock(symbol, amount)

    def add_amount(self, amount):
        self._amount += amount

    def remove_amount(self, amount):
        res = self._amount - amount
        self._amount = res if res > 0 else 0
class StockTransaction(Stock):
    def __init__(self, stock, is_selling, price, timeout):
        super().__init__(stock.symbol, stock.amount)
        self._is_selling = is_selling
        self._price = price
        self._timeout = timeout
    
    @property
    def is_selling(self):
        return self._is_selling
    @property
    def price(self):
        return self._price
    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, val):
        self._timeout = val

    def __str__(self):
        transaction = " VENDA " if self.is_selling else " COMPRA"
        return f"{super().__str__()} {transaction} por {self.price} cada."
    def __repr__(self):
        rep = (self.amount,self.price,self.timeout)
        return f"<StockTransaction>({self.symbol}:{self.price}*{self.amount} por {self.timeout}s)"
    
    @staticmethod
    def from_dict(data):
        symbol = data.get('_symbol')
        amount = data.get('_amount')
        s = Stock(symbol, amount)
        is_selling = data.get('_is_selling')
        price = data.get('_price')
        timeout = data.get('_timeout')

        return StockTransaction(s, is_selling, price, timeout)

    @staticmethod
    def get_from_user(owned_stocks):
        symbol = input("Informe nome do símbolo: ").upper()
        amount = int(input("Quantidade de ações: "))
        print("Tipo pode ser: compra ou venda")
        print("Para compra digite 1, para venda digite 2")
        is_selling = True if int(input("Informe o tipo(1/2): ")) == 2 else False
        # Caso  a transação seja de venda
        if is_selling :
            # Verifica se tem as ações do mesmo símbolo
            # Retorna uma lista, mas tem no maximo um item, pois as ações do mesmo símbolo sempre são agrupadas
            owned_stock = [s for s in owned_stocks if s.symbol == symbol]
            if owned_stock == []:
                print(f"Você não tem ações de {symbol}")
                return None
            # Verifica se tem o suficiente
            elif owned_stock[0].amount < amount:
                print(f"Você tem apenas {owned_stock[0].amount} ações de {symbol}")
                return None

        print("Preço alvo. Use '.' para separar casas decimais.")
        price = float(input("Preço alvo(R$): "))
        
        print("Quanto tempo deseja manter a ação em estado condicional?")
        timeout = float(input("Tempo(s): "))
        # Retorna em formato dict
        d = {
            '_symbol': symbol,
            '_amount':amount,
            '_is_selling':is_selling,
            '_price':price,
            '_timeout':timeout
        }
        return d

    def can_trade(self, other):
        # Usa o operador sobrecarregado de comparação
        # Mesmo símbolo e mesma quantidade
        if self == other:
            # Se um vende e o outro compra
            if self.is_selling == (not other.is_selling):
                # Mesmo preço
                if self.price == other.price:
                    return True
        return False

    def update_timeout(self):
        if self.timeout > 0:
            self.timeout -= 1
        return self.timeout

if __name__ == "__main__":
    apple = Stock("NADASQ", "AAPL", 15)
    apple2 = Stock("NADASQ", "AAPL", 17)
    t_apple = StockTransaction(apple, True, 120, 0)
    t_apple2 = StockTransaction(apple2, False, 56, 0)
    print(apple)
    print(apple2)
    print("***************")
    print(t_apple)
    print(t_apple2)
    t_apple.trade(t_apple2)



