import Pyro4

@Pyro4.expose
class Subscription(object):
  UPPER_LIMIT = 1
  LOWER_LIMIT = 2
  def __init__(self, company, limit_type, trigger):
    # A empresa cuja ações são relevantes para objeto
    self._company = company
    # Tipo de evento a ser analisado 
    # Pode ser UPPER_LIMIT ou LOWER_LIMIT
    self._limit_type = limit_type
    self._trigger = trigger
  def __str__(self):
    limit_type = "Limite de ganho" if self._limit_type == self.UPPER_LIMIT else "Limite de perda"
    return "Evento sobre {0} do tipo {1} com preço alvo {2}".format(self._company.name, limit_type, self._trigger)