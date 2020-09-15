"""Funções para manipular uma inscrição em evento, representada por um dicionário com chaves: 'company', 'upper_limit' e 'lower_limit' """
import company as StockCompany

# Representa o tipo de evento limite de ganho
UPPER_LIMIT_TYPE = 1
# Representa o tipo de evento limite de perda
LOWER_LIMIT_TYPE = 2

def createSubscription(company, upper_limit, lower_limit):
    if StockCompany.isValidCompany(company):
        subscription = {
            'company': company,
            'upper_limit': upper_limit,
            'lower_limit': lower_limit
        }
        return subscription
    else:
        print(f"Argumento em createSubscription não é uma empresa válida")
        exit()

def isValidSubscription(subscription):
    hasAllKeys = all(key in subscription for key in (
        "company", "upper_limit", "lower_limit"))
    return hasAllKeys

def getSubscriptionFromUser(market):
    company = StockCompany.getCompanyFromUser(market)
    print("Limite de ganho. Use '.' para separar casas decimais.")
    upper_limit = float(input("Preço alvo(R$): "))
    print("Limite de perda. Use '.' para separar casas decimais.")
    lower_limit = float(input("Preço alvo(R$): "))
    return createSubscription(company, upper_limit, lower_limit)

def printSubscription(subscription):
    if isValidSubscription(subscription):
        print(f"Evento para {subscription['company']['name']:<4} limites: R${subscription['lower_limit']}, R${subscription['upper_limit']}")
    else:
        print(f"Argumento em printSubscription não é uma inscrição válida")
        exit()
