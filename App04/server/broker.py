from random import randint
from market import Market
from typing import List

from flask import Response

class Broker(object):
  def __init__(self, client : str, market : Market):
    self.client_id : str = client
    self.market : Market = market
    self.topics : dict = {}
    self.giveInitialStocks()
    print(f"Broker for {client} created")

  def giveInitialStocks(self):
    # Chamado na inicializacao do broker
    self.topics['stocks'] = {}
    rand_symbs : list = Market.get_random_symbols(self.market.symbols)
    for s in rand_symbs:
      self.topics['stocks'][s] = randint(1, 5)

  def checkMarketSymbol(self, symb : str) -> bool:
    try:
      self.market.symbols[symb]
      return True
    except KeyError:
      print(f'Problem getting symbol {symb}')
      return False

  def checkTopicSymbol(self, symb : str, topic : str) -> bool:
    try:
      self.topics[topic][symb]
      return True
    except KeyError:
      print(f'Problem getting symbol {symb}')
      return False

  def get(self, topic : str, last_param : str) -> dict:
    if topic not in self.topics:
      # Tentando ler topico inexistente, retorna dict vazio
      self.topics[topic] = {}

    # Monta resposta apropriada
    response : dict = {'data': {}}
    items : List[tuple] = list(self.topics[topic].items())
    symb : str = ""
    if topic == 'quotes':
      # Pega os symbols da carteira, mas apenas os que nao estao na lista items (para nao mostrar duas vezes)
      owned_stocks = [s for s in self.topics['stocks'].items() if s not in items]
      items += owned_stocks
      for quote in items:
        symb = quote[0]
        # O unico jeito de modificar self.topics[topic] eh atraves do metodo addTo
        # Logo temos garantia que os symbols sao validos
        response['data'][symb] = self.market.quote(symb)
    elif topic == 'subscriptions':
      # Se for 'listen' eh requisicao para abrir um canal de notificacoes
      if last_param == 'listen':
        return Response(self.checkSubscriptions(), mimetype='text/event-stream')
      for sub in items:
        symb = sub[0]
        response['data'][symb] = sub[1]
    elif topic == 'stocks':
      for stock in items:
        symb = stock[0]
        response['data'][symb] = stock[1]
    elif topic == 'transactions':
      print("Transactions")
    return response

  def addTo(self, topic : str, msg : dict) -> dict:
    if topic not in self.topics:
      # Tentando adicionar msg em topico que nao existe ainda
      # Inicializa o topico antes. Supoe que o topico eh valido
      self.topics[topic] = {}

    symb : str = msg['symbol']

    # Verifica se symbol eh valido no mercado
    if not self.checkMarketSymbol(symb):
      return {'error': f"Invalid symbol {symb}, ignoring request..."}

    # Trata cada topico de acordo
    if topic == 'quotes':
      self.topics[topic][symb] = self.market.quote(symb)
    elif topic == 'subscriptions':
      self.topics[topic][symb] = (msg['lower'], msg['upper'])
      
    return {'data': self.topics[topic]}

  def removeFrom(self, topic : str, msg : dict) -> dict:
    if topic not in self.topics:
      # Tentando remover msg de topico que nao existe
      return {'error': f'Topic {topic} not found'}

    symb : str = msg['symbol']

    # Verifica se symbol eh valido no mercado
    if not self.checkMarketSymbol(symb):
      return {'error': f"Invalid symbol {symb}, ignoring request..."}
    # O simbolo existe no mercado, mas pode nao existir no topico
    if not self.checkTopicSymbol(symb, topic):
      return {'error': f"Symbol {symb} not found in {topic}, ignoring request..."}

    self.topics[topic].pop(symb)

    return {'data': f'Removed {symb} from {topic}'}

  def checkSubscriptions(self):
    while True:
      if 'subscriptions' in self.topics:
        subscriptions : dict = self.topics['subscriptions']
        items : List[tuple] = list(subscriptions.items())
        for sub in items:
          symb : str = sub[0]
          limits : tuple = sub[1]
          lower : float = float(limits[0])
          upper : float = float(limits[1])
          current_quote : float = self.market.quote(symb)
          if current_quote < lower or current_quote > upper:
            msg : str = f"Symbol {symb} at {current_quote}"
            print(msg)
            subscriptions.pop(symb)
            yield f'data: {msg}\n\n'
        if not len(items):
          self.topics.pop('subscriptions')
