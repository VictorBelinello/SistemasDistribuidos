from flask_restful import abort
from enum import Enum

class ERRORS(Enum):
  RESOURCE_NOT_FOUND = 404
  INVALID_REQUEST = 400

def abort_if(cond, info="No debug info was provided"):
  if cond == ERRORS.RESOURCE_NOT_FOUND:
    abort(404, error_message=f"The resource requested doesn't exist.\nInfo: {info}\n")
  elif cond == ERRORS.INVALID_REQUEST:
    abort(400, error_message=f"The request was invalid.\nInfo:{info}\n")

def verify(req, symbols):
  if not req.is_json or 'symbol' not in req.get_json():
    abort_if(ERRORS.INVALID_REQUEST, "Request must be valid JSON.\nThe field 'symbol' must be defined.")
  s = req.get_json()['symbol']
  if s not in symbols:
    abort_if(ERRORS.RESOURCE_NOT_FOUND, f"The symbol '{s}' is not available.")
  return req.get_json()

def format_sse(data):
  msg = f'data: {data}\n\n'
  return msg