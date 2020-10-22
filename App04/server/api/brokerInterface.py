import requests

class BrokerInterface(object):
  """Classe para realizar o interfaceamento entre  os brokers do sistema"""
  url = "http://127.0.0.1:5000/brokers"

  def get_all_orders(self):
    r = requests.get(self.url)
    # Recupera um json com um unico campo 'data'
    json : dict = r.json()
    # Esse campo contem um vetor de ordens
    orders : list = json['data']
    return orders
  
  def notify_brokers(self, order : tuple, buyer : str, seller : str):
    r = requests.put(self.url, json={'order': order, 'buyer': buyer, 'seller': seller})
    return r.json()

  def send_prepare(self, target : str, tid : str):
    r = requests.put(self.url + f'/{target}', json={'tid': tid})

  def send_commit(self):
    r = requests.put(self.url, json={'data': 'Commit your shit'})
    return r.json()

  def send_abort(self):
    r = requests.put(self.url, json={'data': 'Abort your shit'})
    return r.json()