from key import *
from get_positions import *
from main import *

def get_type(instrument_name):
  x = instrument_name.split('-')[3]
  if x == 'C':
    return 'call'
  elif x == 'P': 
    return 'put'
  else:
    return None
    
def get_expiration_date(instrument_name):
  x = instrument_name.split('-')[1]

def get_portfolio(simulated=False):
  if simulated:
    result = []
    result.append({'name': '1', 'direction': 'buy', 'type': 'call', 'size': 1, 'vega': 0.1, 'delta': 0.5, 'iv': 52, 'price': 350, 'expiration date': 1, 'floating_profit_loss': 0})
    result.append({'name': '2', 'direction': 'buy', 'type': 'call', 'size': 5, 'vega': 0.05, 'delta': 0.2, 'iv': 55, 'price': 900, 'expiration date': 2, 'floating_profit_loss': 0})
    result.append({'name': '3', 'direction': 'buy', 'type': 'put', 'size': 10, 'vega': 0.2, 'delta': -0.1, 'iv': 51, 'price': 620, 'expiration date': 3, 'floating_profit_loss': 0})
    result.append({'name': '4', 'direction': 'sell', 'type': 'put', 'size': 3, 'vega': 0.05, 'delta': -0.2, 'iv': 63, 'price': 250, 'expiration date': 4, 'floating_profit_loss': 0})
    result.append({'name': '5', 'direction': 'sell', 'type': 'put', 'size': 4, 'vega': 0.1, 'delta': -0.5, 'iv': 66, 'price': 150, 'expiration date': 5, 'floating_profit_loss': 0})
    futures = [{'name': 'future 1', 'size': -20000, 'floating_profit_loss': 0, 'direction': 'sell'}, {'name': 'future 2', 'size': 5000, 'floating_profit_loss': 0, 'direction': 'buy'}]
    return result, futures
  positions = get_positions()['result']
  options = [x for x in positions if x['kind'] == 'option']
  futures = [x for x in positions if x['kind'] == 'future']
  options = [{'name': x['instrument_name'], 'price': x['mark_price'], 'size': abs(x['size']), 'direction': x['direction'], 'type': get_type(x['instrument_name']), 'expiration date': get_expiry_date_of_instrument(x['instrument_name']), 'floating_profit_loss': x['floating_profit_loss']} for x in options]
  return options, futures

