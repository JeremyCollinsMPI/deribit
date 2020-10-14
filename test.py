from submit_order import *
from calculate_orders import *
from prepare_values import *
from main import *

def test1():
  random_order = {'instrument_name': 'E', 'price': str(0.0001), 'amount': str(1)}
  return submit_order(random_order, test_host)

def test2():
  random_portfolio = {}
  instrument_names = find_instruments_to_query()
  return str(calculate_orders(random_portfolio, instrument_names, show_calculations=True))

def test3():
  random_portfolio = {}
  instrument_names = get_instruments()
  return str(calculate_orders(random_portfolio, instrument_names, show_calculations=True, simulated=True))

def test4():
  return prepare_values(simulated=True)




