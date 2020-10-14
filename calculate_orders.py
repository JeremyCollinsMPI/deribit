import json 
from get_positions import *
import requests
from model import *
from get_instruments import *
from get_portfolio import *
from prepare_values import *

def get_risk_limits():
  file = open('risk_limits.json', 'r')
  return json.load(file)

def vega_option_calculations(portfolio, price_of_bitcoin):
  vegas = np.array([x['vega'] for x in portfolio])
  sizes = np.array([x['size'] for x in portfolio])
  directions = [x['direction'] for x in portfolio]
  directions_numerical = [float(-1) if x == 'sell' else float(1) if x == 'buy' else float(0) for x in directions]
  directions_numerical = np.array(directions_numerical)
  dollar_vega = directions_numerical * price_of_bitcoin * sizes * vegas 
  aggregate_vega = np.sum(dollar_vega)
  result = {'vega aggregate': round(aggregate_vega, 2)}
  return result
  
def get_vega_positioning(simulated=False):
  options, futures = get_portfolio(simulated)
  portfolio = options
  if options == []:
    return 0
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
  result = vega_option_calculations(portfolio, price_of_bitcoin)
  return result['vega aggregate']
  
def get_vega_risk_overlay(risk_limits, simulated=False):
  vega_positioning = get_vega_positioning(simulated)
  if vega_positioning < float(risk_limits["Zero skew upper"]):
    return 0
  if vega_positioning >= float(risk_limits["Zero skew upper"]) and vega_positioning < float(risk_limits["Medium skew upper"]):
    vega_skew = float(risk_limits["Medium skew rate of skew"])
    if vega_positioning > 0:
      return vega_skew * (vega_positioning - float(risk_limits["Zero skew upper"]))
    else: 
      return vega_skew * (vega_positioning - float(risk_limits["Zero skew upper"])) * -1
  if vega_positioning >= float(risk_limits["Medium skew upper"]):
    vega_skew = float(risk_limits["Fast skew rate of skew"])
    if vega_positioning > 0: 
      return vega_skew * (vega_positioning - float(risk_limits["Medium skew upper"]))
    else:
      return vega_skew * (vega_positioning - float(risk_limits["Medium skew upper"])) * -1

def filter_of_implied_volatility_risk_limits_bid(risk_limits, final_price, best_bid, min_price_increment):
  difference = final_price - best_bid
  if difference < risk_limits['No quote upper']:
     return False, 0
  elif difference >= risk_limits['No quote upper'] and difference < risk_limits["Best price upper"]:
    return True, best_bid + min_price_increment
  elif difference > risk_limits["Best price upper"]:
    return True, final_price - risk_limits["Best price upper"]


def filter_of_implied_volatility_risk_limits_ask(risk_limits, final_price, best_ask, min_price_increment):
  difference = best_ask - final_price
  if difference < risk_limits['No quote upper']:
     return False, 0
  elif difference >= risk_limits['No quote upper'] and difference < risk_limits["Best price upper"]:
    return True, best_ask - min_price_increment
  elif difference > risk_limits["Best price upper"]:
    return True, final_price + risk_limits["Best price upper"]


def find_bid_amount(final_price, price, best_bid, risk_limits, best_bid_amount):
  step1 = final_price - price
  step2 = step1 - risk_limits['No quote upper']
  step3 = step2 / (risk_limits['Best price upper'] - risk_limits['No quote upper'])
  step4 = step3 * best_bid_amount
  return min(risk_limits['Max size'], step4)

def find_ask_amount(final_price, price, best_ask, risk_limits, best_ask_amount):
  step1 = price - final_price
  step2 = step1 - risk_limits['No quote upper']
  step3 = step2 / (risk_limits['Best price upper'] - risk_limits['No quote upper'])
  step4 = step3 * best_ask_amount
  return min(risk_limits['Max size'], step4)

def calculate_orders(instrument_names, show_calculations=False, simulated=False, simulated_portfolio=False):
  result = []
  if simulated:
    instrument_names = ['simulated option']
  risk_limits = get_risk_limits()
  vega_risk_overlay = get_vega_risk_overlay(risk_limits, simulated_portfolio)
  manual_overlay = 1
  min_price_increment = 0.1
  for instrument_name in instrument_names:
    model_prediction = get_model_prediction(instrument_name, simulated)
    if model_prediction == 'No asks or bids':
      continue
    final_price = model_prediction + vega_risk_overlay + manual_overlay
    weighted_order_book_price = get_weighted_order_book_price(instrument_name, simulated=simulated)
    if weighted_order_book_price == 'No asks or bids':
      continue
    best_bid = get_best_bid(instrument_name, simulated=simulated)
    best_bid_amount = get_best_bid_amount(instrument_name, simulated=simulated)   
    passes_filter_of_implied_volatility_risk_limits, price = filter_of_implied_volatility_risk_limits_bid(risk_limits, final_price, best_bid, min_price_increment)
    if passes_filter_of_implied_volatility_risk_limits:
      amount = find_bid_amount(final_price, price, best_bid, risk_limits, best_bid_amount)
      temp_result = {'instrument_name': instrument_name, 'price': price, 'amount': amount, 'type': 'buy'}
      if show_calculations:
        result.append(temp_result)
        historic_price = get_historic_price(instrument_name, show_calculations=show_calculations, simulated=simulated)
        temp_result.update({'model prediction': model_prediction, 'best bid': best_bid, 'difference': final_price - best_bid, 'best bid + min price increment': best_bid + min_price_increment, 'fixed price': final_price - risk_limits["Best price upper"], 'price': price, 'historic price': historic_price, 'vega risk overlay': vega_risk_overlay, 'weighed order book price': weighted_order_book_price, 'final price': final_price})
      result.append(temp_result)
    best_ask = get_best_ask(instrument_name, simulated=simulated)
    best_ask_amount = get_best_ask_amount(instrument_name, simulated=simulated)   
    passes_filter_of_implied_volatility_risk_limits, price = filter_of_implied_volatility_risk_limits_ask(risk_limits, final_price, best_ask, min_price_increment)
    if passes_filter_of_implied_volatility_risk_limits:
      amount = find_ask_amount(final_price, price, best_ask, risk_limits, best_ask_amount)
      temp_result = {'instrument_name': instrument_name, 'price': price, 'amount': amount, 'type': 'sell'}
      if show_calculations:
        result.append(temp_result)
        historic_price = get_historic_price(instrument_name, show_calculations=show_calculations, simulated=simulated)
        temp_result.update({'model prediction': model_prediction, 'best ask': best_ask, 'difference': best_ask - final_price, 'best ask - min price increment': best_bid - min_price_increment, 'fixed price': final_price + risk_limits["Best price upper"], 'price': price, 'historic price': historic_price, 'vega risk overlay': vega_risk_overlay, 'weighted order book price': weighted_order_book_price, 'final price': final_price})
      result.append(temp_result)  
  return result

