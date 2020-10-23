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

  def send_to(self, target: str, tid : str, action : str):
    r = requests.put(self.url + f'/{target}', json={'tid': tid, 'action': action})
    json : dict = r.json()
    ans : bool = json.get('data')
    return ans

  def send_can_commit(self, target : str, tid : str):
    return self.send_to(target, tid, 'prepare')

  def send_commit(self, target : str, tid : str):
    return self.send_to(target, tid, 'commit')

  def send_abort(self, target : str, tid : str):
    return self.send_to(target, tid, 'abort')