import numpy as np
from get_last_trades import *
import time


def get_best_bid(instrument_name, simulated=False):
  r = requests.get('https://www.deribit.com/api/v2/public/get_order_book?instrument_name='+instrument_name)
  dict = r.json()
  if simulated:
    return 53
  return dict['result']['bid_iv']

def get_best_bid_amount(instrument_name, simulated=False):
  r = requests.get('https://www.deribit.com/api/v2/public/get_order_book?instrument_name='+instrument_name)
  dict = r.json()
  if simulated:
    return 25
  return dict['result']['best_bid_amount']

def get_best_ask(instrument_name, simulated=False):
  r = requests.get('https://www.deribit.com/api/v2/public/get_order_book?instrument_name='+instrument_name)
  dict = r.json()
  if simulated:
    return 60
  return dict['result']['ask_iv']
  
def get_best_ask_amount(instrument_name, simulated=False):
  r = requests.get('https://www.deribit.com/api/v2/public/get_order_book?instrument_name='+instrument_name)
  dict = r.json()
  if simulated:
    return 20
  return dict['result']['best_ask_amount']

def get_weighted_order_book_price(instrument_name, simulated=False):
  r = requests.get('https://www.deribit.com/api/v2/public/get_order_book?instrument_name='+instrument_name)
  dict = r.json()
  if simulated:
    best_ask = 60
    best_ask_amount = 20 
    best_bid = 53
    best_bid_amount = 25
  else:
    best_ask = dict['result']['ask_iv']
    best_ask_amount = dict['result']['best_ask_amount']  
    best_bid = dict['result']['bid_iv']
    best_bid_amount = dict['result']['best_bid_amount']
  if best_ask_amount + best_bid_amount == 0:
    return 'No asks or bids'
  return ((best_ask * best_ask_amount) + (best_bid * best_bid_amount)) / (best_ask_amount + best_bid_amount)
    
def get_historical_prices(instrument_name, simulated=False):
  current_timestamp = int(time.time() * 1000)
  milliseconds_in_a_day = 1000*60*60*24
  start_timestamp = current_timestamp - milliseconds_in_a_day
  initial = get_last_trades_by_time(instrument_name, start_timestamp=start_timestamp, count=1000)
  def get_how_long_ago_in_hours(number_in_milliseconds):
    return number_in_milliseconds / (1000*60*60)
  if simulated:
    return [{'How long ago': 1, 'Volume': 10, 'Price': 53}, {'How long ago': 5, 'Volume': 30, 'Price': 52}, {'How long ago': 23, 'Volume': 20, 'Price': 55}]
  try:
    trades = initial['result']['trades']
    result = [{'How long ago': get_how_long_ago_in_hours(current_timestamp - x['timestamp']), 'Volume': x['amount'], 'Price': x['iv']} for x in trades]
    return result
  except:
    return []

def get_historic_price(instrument_name, show_calculations=False, simulated=False):
  historical_prices = get_historical_prices(instrument_name, simulated=simulated)
  volumes = np.array([x['Volume'] for x in historical_prices])
  volume_weightings = volumes / np.sum(volumes)
  how_long_ago = np.array([x['How long ago'] for x in historical_prices])
  coefficients = (24 - how_long_ago)/24
  time_weightings = coefficients / np.sum(coefficients)
  weightings = (volume_weightings + time_weightings) / 2
  prices = np.array([x['Price'] for x in historical_prices])
  if show_calculations:
    return {'sum': np.sum(prices * weightings), 'prices': prices, 'weightings': weightings}
  return np.sum(prices * weightings)

def get_model_prediction(instrument_name, simulated=False):
  weightings = [0.75, 0.25]
  order_book_price = get_weighted_order_book_price(instrument_name, simulated=simulated)
  historic_price = get_historic_price(instrument_name, simulated=simulated)
  if order_book_price == 'No asks or bids':
    return 'No asks or bids'
  return (weightings[0] * order_book_price) + (weightings[1] * historic_price)

