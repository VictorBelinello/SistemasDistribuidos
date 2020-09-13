def new_stock(company, quantity):
  stock = {}
  stock["company"] = company
  stock["quantity"] = quantity
  return stock

def to_string(s):
  # Retorna uma string ou lista de strings dependendo se 's' eh uma lista de stocks ou apenas uma
  if isinstance(s, list):
    strs = []
    for stock in s:
      strs.append(f"[{stock['company']:<5}] : {stock['quantity']}")
    return strs
  elif isinstance(s, dict):
    return f"[{s['company']:<5}] : {s['quantity']}"

def print_stock(s):
  strs = to_string(s) # resultado pode ser lista de strings ou uma string apenas
  if isinstance(strs, list):
    for stock_str in strs:
      print(stock_str)
  else:
    print(strs)