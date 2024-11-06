
import json
from urllib.parse import quote

def encode_params_url(params):
  json_string = json.dumps(params)
  encoded_string = quote(json_string)
  return encoded_string
