from flask import Flask, render_template, request, redirect
import json
from prepare_values import *
from werkzeug.datastructures import ImmutableMultiDict
from time import sleep
from test import *

app = Flask(__name__)

@app.route('/v1/')
def render_static():
    dictionary = prepare_values(simulated=True)
    return render_template('v1.html', dictionary = dictionary)

@app.route('/test_v1/')
def test_v1():
#     dictionary = prepare_values()
    dictionary = test4()
    return render_template('v1.html', dictionary = dictionary)


@app.route('/risk_limits/')
def render_static_risk_limits():
    file = open('risk_limits.json', 'r')
    dictionary = json.load(file)
    return render_template('risk_limits.html', dictionary = dictionary)
    
@app.route('/test_submit_order')
def test_submit_order():
    return test1()

@app.route('/test_show_orders_given_portfolio')
def test_show_orders_given_portfolio():
    return str(test2())
    
@app.route('/test_show_orders_given_portfolio_simulated')
def test_show_orders_given_portfolio_simulated():
    return str(test3())
    
@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      result = result.to_dict(flat=True)
      file = open('risk_limits.json', 'w')
      json.dump(result, file)
      file.close()
      return redirect(home)

if __name__ == '__main__':
    app.run(host='0.0.0.0')