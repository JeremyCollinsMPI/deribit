import requests
from key import *
from calculate_orders import *

host = 'https://www.deribit.com/api/v2/private/'
# test_host = 'https://test.deribit.com/api/v2/private/'
call = 'buy'


def submit_order(order, host, type):
  r = requests.get(host+type+'?'+'instrument_name='+order['instrument_name']+'&'+'price='+order['price']+'&'+'amount='+order['amount'], headers={'Authorization': 'Basic ' + base64})
  return r.json()

order = {'instrument_name': 'BTC-4MAR20-8000-C', 'price': 0.01, 'amount': 1}
r = requests.get(host+type+'?'+'instrument_name='+order['instrument_name']+'&'+'price='+order['price']+'&'+'amount='+order['amount'], headers={'Authorization': 'Basic ' + base64})
type = 'buy'
