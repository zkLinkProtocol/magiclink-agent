from httpx import Client
import base64
import datetime
import hmac
import json

class OKX(Client):
  def __init__(self):
    super().__init__(base_url='https://www.okx.com')
    self.API_ACCESS_KEY = 'c2e47c18-1e37-4141-85bb-25894f2ba7e7'
    self.API_SECRET_KEY = 'EA774247D00620B281456361514BF59A'
    self.PASSPHRASE = '8686Qwe!'
    self.PROJECT = '3bdbd16edddeb5eb22515dc8b447bea6'
    with open('okx_swap.json') as f:
      self.TOKEN = json.load(f)
  
  def sign(self, message):
    mac = hmac.new(bytes(self.API_SECRET_KEY, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)

  def get_header(self, sign, timestamp):
    return {
      'Content-Type': 'application/json',
      'OK-ACCESS-KEY': self.API_ACCESS_KEY,
      'OK-ACCESS-SIGN': str(sign),
      'OK-ACCESS-TIMESTAMP': timestamp,
      'OK-ACCESS-PASSPHRASE': self.PASSPHRASE,
      'OK-ACCESS-PROJECT': self.PROJECT,
    }

  def get_timestamp(self):
    now = datetime.datetime.now(datetime.timezone.utc)
    t = now.isoformat("T", "milliseconds")
    return t[:-6] + "Z"
  
  def req(self, method, request_path, params={}):
    response = None
    timestamp = self.get_timestamp()
    if method == 'GET':
      sign = self.sign(f'{timestamp}{method}{request_path}')
      header = self.get_header(sign, timestamp)
      response = self.get(request_path, headers=header)
    else:
      body = json.dumps(params)
      sign = self.sign(f'{timestamp}{method}{request_path}{body}')
      header = self.get_header(sign, timestamp)
      response = self.post(request_path, data=body, headers=header)
    return response.json()

if __name__ == "__main__":
  okx = OKX()
  print(json.dumps(okx.req('GET', '/api/v5/dex/aggregator/supported/chain')))
