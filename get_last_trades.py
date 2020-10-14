import requests
import json


host = 'https://www.deribit.com/api/v2/public/'



def get_last_trades(instrument_name, count=1):
  call = 'get_last_trades_by_instrument'
  r = requests.get(host+call+'?'+'instrument_name='+instrument_name+'&'+'count='+str(count)+'&sorting=desc')
  return r.json()

def get_last_trades_by_time(instrument_name, start_timestamp, count=1):
  call = 'get_last_trades_by_instrument_and_time'
  r = requests.get(host+call+'?'+'instrument_name='+instrument_name+'&'+'count='+str(count)+'&sorting=desc'+'&start_timestamp=' +str(start_timestamp))
  return r.json()


