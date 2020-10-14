from time import sleep
from get_instruments import *
from datetime import date
import calendar
from calculate_orders import *
import requests
import operator


def get_expiry_date_of_instrument(instrument_name):
  months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
  date1 = instrument_name.split('-')[1]
  if date1 == 'PERPETUAL':
    return None
  date2 = date1
  i = 0
  for member in months:
    if member in date1:
      month = member
    date2 = date2.replace(member, 'MONTH')
  day = date2.split('MONTH')[0]
  year = '20' + date2.split('MONTH')[1]
  month = months.index(month) + 1
  result = date(year=int(year), month=int(month), day=int(day))
  timestamp = calendar.timegm(result.timetuple())
  return timestamp

def get_delta_of_instrument(instrument_name):
  r = requests.get('https://www.deribit.com/api/v2/public/get_order_book?instrument_name='+instrument_name)
  dict = r.json()
  return dict['result']['greeks']['delta']

def get_type(instrument_name):
  return instrument_name.split('-')[3]

 
def get_the_options_to_query(result):
  new = []
  number_of_distinct_timestamps = 1
  number_of_deltas_per_type = 2
  current_timestamp = 0
  current_type = ''
  timestamp_count = 0
  delta_count = 0
  for member in result:
    if not member[1] == current_timestamp and timestamp_count == number_of_distinct_timestamps:
      break
    else:
      timestamp_count = timestamp_count + 1
    if member[2] == current_type and delta_count == number_of_deltas_per_type:
      continue
    elif not member[2] == current_type:
      delta_count = 0
    new.append(member[0])
    delta_count = delta_count + 1
    current_timestamp = member[1]
    current_type = member[2]
  return new

def find_instruments_to_query():
  instruments = get_instruments()
  timestamps = [get_expiry_date_of_instrument(x) for x in instruments]
  timestamps = [x for x in timestamps]
  result = list(zip(instruments, timestamps))
  result = [x for x in result if not x[1] == None]
  result = sorted(result, key = operator.itemgetter(1))
  first_timestamp = result[0][1]
  result = [x for x in result if x[1] == first_timestamp]
  instruments = [x[0] for x in result]
  timestamps = [x[1] for x in result]
  deltas = [get_delta_of_instrument(x) for x in instruments]
  deltas_distance_from_0_point_5 = [abs(x - 0.5) for x in deltas]
  types = [get_type(x) for x in instruments]
  result = list(zip(instruments, timestamps, types, deltas_distance_from_0_point_5))
  result = [x for x in result if not x[1] == None]
  result = sorted(result, key = operator.itemgetter(1, 2, 3))
  options_to_query = get_the_options_to_query(result)
  return options_to_query

if __name__ == '__main__':
  while True:
    result = find_instruments_to_query()
    print(result)
    orders = calculate_orders(result)
    print(orders)
    sleep(5)



