"""Funções para manipular uma empresa, representada por um dicionário com chaves: 'name' e 'stock_value'"""
import random
import os
import stock as Stock

class Company(object):
    def __init__(self, name, stock_value):
        self._name = name
        self._stock_value = stock_value
    
    def get

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
        random_value = Stock.getRandomStockValue()
        company = createCompany(name, random_value)
        companies.append(company)
    return companies
