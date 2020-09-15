from client import StockClient
from company import getDefaultCompanies
from market import StockMarket

import stock

def main():
  market = StockMarket("Bolsa de valores", getDefaultCompanies())

  buyer = StockClient("Victor")
  seller = StockClient("Roger")

  try:
    buyer.addStockMarket(market)
    seller.addStockMarket(market)

    print("Ações do comprador")
    buyer.getStocks()
    print("\n")
    print("Ações do vendedor")
    seller.getStocks()
    print("*"*30)

    buyer.addDebugTransaction(seller.stocks_owned[0],stock.BUY_STOCK_TYPE)
    seller.addDebugTransaction(seller.stocks_owned[0],stock.SELL_STOCK_TYPE)
    #buyer.addDebugTransaction(seller.stocks_owned[1],stock.BUY_STOCK_TYPE)
    #seller.addDebugTransaction(seller.stocks_owned[1],stock.SELL_STOCK_TYPE)


    input("ENTER")
    
    print("Ações do comprador")
    buyer.getStocks()
    print("\n")
    print("Ações do vendedor")
    seller.getStocks()
    print("*"*30)
    #client.showMenu()
  except Exception as e:
    print(f"{type(e)}: {e}\n{e.args}")


if __name__ == "__main__":
    main()