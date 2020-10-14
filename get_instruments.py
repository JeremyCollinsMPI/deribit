import requests
import json


host = 'https://www.deribit.com/api/v2/public/'

def get_instruments():
  call = 'get_instruments'
  currency = 'BTC'
  r = requests.get(host+call+'?currency='+currency)
  array = r.json()['result']
  array = [x['instrument_name'] for x in array]
  return array

