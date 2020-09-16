
class Subscription(object):
    def __init__(self, symbol, upper_limit, lower_limit):
        self._symbol = symbol
        self._upper_limit = upper_limit
        self._lower_limit = lower_limit

    @staticmethod
    def from_tuple(data):
        symbol = data[0]
        upper_limit = data[1]
        lower_limit = data[2]
        return Subscription(symbol, upper_limit, lower_limit)

    @staticmethod
    def get_from_user():
        symbol = input("Informe nome do símbolo: ").upper()
        print("Limite de ganho. Use '.' para separar casas decimais.")
        upper_limit = float(input("Preço alvo(R$): "))
        print("Limite de perda. Use '.' para separar casas decimais.")
        lower_limit = float(input("Preço alvo(R$): "))
        return (symbol, upper_limit, lower_limit)

    def __str__(self):
        return f"Evento para ação de {self._symbol} fora dos limites: [{self._lower_limit}, {self._upper_limit}]"