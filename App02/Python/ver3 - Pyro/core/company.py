"""Funções para manipular uma empresa, representada por um dicionário com chaves: 'name' e 'stock_value'"""
import random
import os

def createCompany(name, stock_value):
    company = {
        'name': name,
        'stock_value': stock_value
    }
    return company

def isValidCompany(company):
    return all(key in company for key in (
        "name", "stock_value"))

def getCompanyFromUser(market):
    """Recebe um objeto StockMarket representando a bolsa que contem as empresas."""
    input_name = input("Informe nome da empresa: ").upper()
    companies = market.getAllCompanies()
    names = [c['name'] for c in companies]
    
    while input_name not in names:
        print("A empresa informada não está na bolsa. Aqui estão as empresas disponíveis: ")
        print(names)
        input("Enter para tentar novamente")
        input_name = input("Informe nome da empresa: ").upper()
    return [c for c in companies if c['name'] == input_name][0]


def printCompany(company):
    if isValidCompany(company):
        print(f"{company['name']:<4} valendo R$ {company['stock_value']:.2f}")
    else:
        print(f"Argumento em printCompany não é uma empresa válida")
        exit()

def getDefaultCompanies():
    names = ["AAPL", "CSCO", "MSFT", "GOOG", "IBM", "HPQ", "BP", "FBOK34", "A1MD34", "NVDC34", "TSLA34"]
    companies = []
    for name in names:
        random_value = getRandomStockValue()
        company = createCompany(name, random_value)
        companies.append(company)
    return companies

"""Funções para manipular uma ação, representada por um dicionário com chaves: 'company', 'type', 'amount' , 'target_price' e 'conditional_timeout'"""

BUY_STOCK_TYPE = 1
SELL_STOCK_TYPE = 2
OWNED_STOCK_TYPE = 3

#TODO: APENAS DEBUG
def getDebugTransaction(stock, type):
    company = stock['company']
    amount = 1
    type = type
    target_price = getRandomStockValue()
    conditional_timeout = random.randint(0, 10)
    return createStock(company, amount, type, target_price, conditional_timeout)

def debug(stock):
    for item in stock.items():
        print(item)

def createStock(company, amount, type=OWNED_STOCK_TYPE, target_price=-1, conditional_timeout=-1):
    if isValidCompany(company):
        stock = {
            'company': company,
            'type': type,
            'amount': amount,
            'target_price': target_price,
            'conditional_timeout': conditional_timeout
        }
        return stock
    else:
        print(f"Argumento em createStock não é uma empresa válida")
        exit()

def isValidStock(stock):
    hasAllKeys = all(key in stock for key in (
        "company", "type", "amount", "target_price", "conditional_timeout"))
    return hasAllKeys

def giveRandomStocks(market):
    INITIAL_AMOUNT = 3
    companies = market.getAllCompanies()
    # Sample é equivalente a choices, mas sem repetição
    choices = random.sample(companies, k=INITIAL_AMOUNT)
    amounts = random.choices(range(1, 11), k=INITIAL_AMOUNT)
    stocks = []
    for i in range(INITIAL_AMOUNT):
        s = createStock(choices[i], amounts[i])
        stocks.append(s)
    return stocks


def getStockTransactionFromUser(market):
    company = getCompanyFromUser(market)
    amount = int(input("Quantidade de ações: "))

    print("Tipo pode ser: compra ou venda")
    print("Para compra digite 1, para venda digite 2")
    type = int(input("Informe o tipo(1/2): "))

    print("Preço alvo. Use '.' para separar casas decimais.")
    target_price = float(input("Preço alvo(R$): "))
    
    print("Quanto tempo deseja manter a ação em estado condicional? Expirado o tempo ela será vendida/comprada imediatamente.")
    conditional_timeout = float(input("Tempo(s): "))
    
    return createStock(company, amount, type , target_price, conditional_timeout)

def canDoStockTransaction(stock_transaction, stocks_owned):
    """Verifica se a partir da lista stocks_owned, é possível realizar a transação stock_transaction"""
    company = stock_transaction['company']['name']
    for stock in stocks_owned:
        # Encontrou ações da empresa
        if stock['company']['name']  == company:
            # Tem no mínimo a quantidade de ações que deseja vender
            if stock['amount'] >= stock_transaction['amount']:
                return True
            return False
    return False

def printStock(stock):
    if isValidStock(stock):
        if stock['type'] == OWNED_STOCK_TYPE:
            type_str = "ADQUIRIDA"
        else:
            type_str = "COMPRA " if stock['type'] == BUY_STOCK_TYPE else "VENDA"
        print(f"{stock['amount']} ações de {stock['company']['name']:<5} - Tipo: {type_str}")
    else:
        print(f"Argumento em printStock não é uma ação válida")
        exit() 

def getRandomStockValue():
    return round(random.uniform(5, 200), 2)