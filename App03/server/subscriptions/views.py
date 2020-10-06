from flask import abort, Response, request

from ..market import default_market
from . import subscriptions_bp

from server.common import get_data, make_response

SUBSCRIPTIONS = {}
@subscriptions_bp.route('/stream', methods=['GET'])
def stream(id):
  if id not in SUBSCRIPTIONS:
    SUBSCRIPTIONS[id] = []
  response = Response(check_subscriptions(id), mimetype="text/event-stream")
  return response


def should_notify(subscription):
  symb = subscription['symbol']
  lower = float(subscription['lower'])
  upper = float(subscription['upper'])
  quote = default_market.quote(symb)

  if quote < lower or quote > upper:
    return True
  return False

def check_subscriptions(id):
  while True:
    for subscription in SUBSCRIPTIONS[id]:
      if should_notify(subscription):
        symb = subscription['symbol']
        response = f'data: {symb} atingiu {default_market.quote(symb)}\n\n'
        # Remove inscricao do evento
        SUBSCRIPTIONS[id].remove(subscription)
        yield response

@subscriptions_bp.route('', methods=['POST'])
def post(id):
  if id not in SUBSCRIPTIONS:
    SUBSCRIPTIONS[id] = []

  status, data = get_data(request)
  if status != 200:
    return make_response(status, data)
  # Adiciona data na lista de inscricoes do usuario 'id'
  SUBSCRIPTIONS[id].append(data)
  return make_response(200, data)

