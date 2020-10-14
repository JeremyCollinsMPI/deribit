from get_portfolio import *
import requests
import numpy as np

  
def get_order_book(name):
  r = requests.get('https://www.deribit.com/api/v2/public/get_order_book?instrument_name='+name)
  return r.json()

def get_price_of_bitcoin():
  r = requests.get('https://www.deribit.com/api/v2/public/get_index?currency=BTC')
  return r.json()['result']['BTC']

def option_calculations(portfolio, price_of_bitcoin):
  vegas = np.array([x['vega'] for x in portfolio])
  expiration_dates = [x['expiration date'] for x in portfolio]
  vegas_by_expiration_date = list(zip(vegas, expiration_dates))
  vegas_by_expiration_date = sorted(vegas_by_expiration_date, key=lambda x: x[1])
  vega_dictionary = {}
  try:
    vega_dictionary['vega nearest'] = vegas_by_expiration_date[0][0]
  except:
    vega_dictionary['vega nearest'] = 0
  for i in range(5):
    try:
      vega_dictionary['vega t+' + str(i)] = vegas_by_expiration_date[i][0]
    except:
      vega_dictionary['vega t+' + str(i)] = 0
  deltas = np.array([x['delta'] for x in portfolio])
  sizes = np.array([x['size'] for x in portfolio])
  directions = [x['direction'] for x in portfolio]
  directions_numerical = [-1 if x == 'sell' else 1 if x == 'buy' else 0 for x in directions]
  directions_numerical = np.array(directions_numerical)
  dollar_delta = directions_numerical * price_of_bitcoin * sizes * deltas
  options = np.sum(dollar_delta)
  aggregate_delta = options
  dollar_vega = directions_numerical * price_of_bitcoin * sizes * vegas 
  aggregate_vega = np.sum(dollar_vega)
  result = {'aggregate delta': round(aggregate_delta, 2), 'vega aggregate': round(aggregate_vega, 2)}
  result.update(vega_dictionary)
  deltas_and_directions = list(zip(dollar_delta, directions))
  deltas_bought = [x[0] for x in deltas_and_directions if x[1] == 'buy']
  deltas_sold = [x[0] for x in deltas_and_directions if x[1] == 'sell']
  result['total bought'] = round(np.sum(deltas_bought), 2)
  result['total sold'] = round(np.sum(deltas_sold), 2)
  buy_iv = np.array([x['iv'] for x in portfolio if x['direction'] == 'buy'])
  buy_sizes = np.array([x['size'] for x in portfolio if x['direction'] == 'buy'])
  buy_vegas = np.array([x['vega'] for x in portfolio if x['direction'] == 'buy'])
  sell_iv = np.array([x['iv'] for x in portfolio if x['direction'] == 'sell'])
  sell_sizes = np.array([x['size'] for x in portfolio if x['direction'] == 'sell'])
  sell_vegas = np.array([x['vega'] for x in portfolio if x['direction'] == 'sell'])
  buy_implied_vol_total = np.sum(buy_iv * buy_sizes * buy_vegas)
  sell_implied_vol_total = np.sum(sell_iv * sell_sizes * sell_vegas)
  buy_vega_no_options_total = np.sum(buy_vegas * buy_sizes)
  sell_vega_no_options_total = np.sum(sell_vegas * sell_sizes)
  result['long volume average price'] = round(buy_implied_vol_total / buy_vega_no_options_total, 2)
  result['short volume average price'] = round(sell_implied_vol_total / sell_vega_no_options_total, 2)
  return result

def get_futures_delta(futures):
  total = 0
  for future in futures:
    total = total + future['size']
  return round(total, 2)

def get_futures_pnl(futures):
  result = []
  for future in futures:
    result.append({'mark to market': round(future['floating_profit_loss'], 2), 'name': future['name']})
  return result

def get_futures_volumes(futures):
  sizes_and_directions = [[x['size'], x['direction']] for x in futures]
  bought_volumes = [x[0] for x in sizes_and_directions if x[1] == 'buy']
  sold_volumes = [x[0] for x in sizes_and_directions if x[1] == 'sell']
  futures_bought_volume = np.sum(bought_volumes)
  futures_sold_volume = np.sum(sold_volumes)
  return round(futures_bought_volume, 2), round(futures_sold_volume, 2)

def prepare_values(simulated=False):
  options, futures = get_portfolio(simulated)
  portfolio = options
  futures_delta = get_futures_delta(futures)
  futures_pnl = get_futures_pnl(futures)
  if options == []:
    result = {'vega nearest': 0, 'vega t+1': 0, 'vega t+2': 0, 'vega t+3': 0, 'vega t+4': 0, 'vega aggregate': 0}
    result['aggregate delta'] = futures_delta
    result['pnl']= futures_pnl
    result['long volume'], result['short volume'] = get_futures_volumes(futures)
    return result
  if not simulated:
    for i in range(len(options)):
      item = portfolio[i]
      data = get_order_book(item['name'])
      print(data)
      try:
        result = data['result']
      except:
        item['delta'] = 'NA'
        item['vega'] = 'NA'
      try:
        greeks = data['result']['greeks']
        item['delta'] = greeks['delta']
        item['vega'] = greeks['vega']
        item['iv'] = data['result']['bid_iv']
      except:
        item['vega'] = 'NA'
        item['delta'] = 'NA'
        item['iv'] = 'NA'
      portfolio[i] = item
  price_of_bitcoin = get_price_of_bitcoin()
  if simulated:
    price_of_bitcoin = 9500
  result = option_calculations(portfolio, price_of_bitcoin)
  result['aggregate delta'] = round(result['aggregate delta'] + futures_delta, 2)
  futures_bought_volume, futures_sold_volume = get_futures_volumes(futures)
  result['long volume'] = round(result['total bought'] + futures_bought_volume, 2)
  result['short volume'] = round((result['total sold'] + futures_sold_volume) * -1, 2)
  result['aggregate position'] = round(result['long volume'] + result['short volume'], 2)
  result['aggregate position average price'] = round(((result['long volume'] * result['long volume average price']) + (result['short volume'] * result['short volume average price'])) / result['aggregate position'], 2)
  result['pnl'] = []
  for member in portfolio:
    result['pnl'].append({'mark to market': round(member['floating_profit_loss'], 2), 'name': member['name']})
  result['pnl'] = result['pnl'] + futures_pnl
  return result
  
