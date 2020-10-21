from ..model.clientModel import ClientModel
from flask import request

class ClientController(object):
  TOPICS = ['quotes', 'subscriptions']
  def __init__(self, model : ClientModel):
    self.model = model

  def get(self, topic : str):
    if topic == 'quotes':
      quotes = self.model.get_quotes()
      return {'data': quotes}
    if topic == 'subscriptions':
      subs = self.model.get_subscriptions()
      return {'data': subs}
    return {'error': f'BAD ROUTE /{topic}'}

  def put(self, topic : str):
    json : dict = request.get_json()
    #self.model.add(topic, json)
    if topic == 'quotes':
      ok, reason = self.model.add_quote(json.get('symbol'))
      return  ({'data': json}, 201) if ok else ({'error': f'PUT failed, reason: {reason}'}, 400)
    if topic == 'subscriptions':
      ok, reason = self.model.add_subscription(json.get('symbol'), json.get('lower'), json.get('upper'))
      return  ({'data': json}, 201) if ok else ({'error': f'PUT failed, reason: {reason}'}, 400)
    return {'error': f'BAD ROUTE /{topic}'}

  def delete(self, topic : str):
    json : dict = request.get_json()
    if topic == 'quotes':
      ok, reason = self.model.del_quote(json.get('symbol'))
      return ({}, 204) if ok  else ({'error': f'DELETE failed, reason: {reason}'}, 400)
    if topic == 'subscriptions':
      ok, reason = self.model.del_subscription(json.get('symbol'), json.get('lower'), json.get('upper'))
      return  ({}, 204) if ok else ({'error': f'DELETE failed, reason: {reason}'}, 400)
    return {'error': f'BAD ROUTE /{topic}'}