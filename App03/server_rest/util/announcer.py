import queue
from flask import Response
from flask_restful import Resource

class Announcer(object):
  def __init__(self):
    self.listeners = []

  def listen(self):
    q = queue.Queue(maxsize=5)
    self.listeners.append(q)
    return q
  
  def announce(self, msg):
    for i in range(len(self.listeners)):
      try:
        self.listeners[i].put_nowait(msg)
      except queue.Full:
        del self.listeners[i]


class AnnouncerView(Resource):
  def __init__(self, announcers):
    self.announcers = announcers

  def get(self, id):
    # Cliente abriu uma conexao para receber notificacoes
    if id not in self.announcers:
      # Cria o announcer que ira fornecer a interface para notificacoes
      self.announcers[id] = Announcer()
    def stream(id):
      # Pega a fila de mensagens especifica do cliente 'id'
      messages = self.announcers[id].listen()
      while True:
        # Bloqueia ate receber uma mensagem na fila
        msg = messages.get() 
        yield msg
    # Quando stream(id) retornar envia a resposta/notificacao para cliente
    return Response(stream(id), mimetype='text/event-stream')
  