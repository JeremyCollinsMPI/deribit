import requests
import json
from key import *

host = 'https://www.deribit.com/api/v2/private/'
call = 'get_positions'
currency = 'BTC'


def get_positions():
  r = requests.get(host+call+'?'+'currency='+currency, headers={'Authorization': 'Basic ' + base64})
  return r.json()

