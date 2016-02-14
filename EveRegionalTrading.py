import os
import xml.etree.ElementTree as ET
import urllib
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

#config
DEBUG      = True
SECRET_KEY = 'development key'

#For the actual program
EVE_ITEMS_CSV = '/home/awbriggs/Development/EveRegionalTrading/eve_items/eve_items.csv'
EVE_ITEMS_NAME_DICT = {}


app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def get_input():
    return render_template('index.html')

@app.route('/report',methods=['POST'])
def add_query():
    EVE_ITEMS_TYPEID_DICT, EVE_ITEMS_NAME_DICT = get_items()

    report_title  = request.form['report_name']
    input_items   = request.form['items_text']
    first_system  = request.form['first_system_id']
    second_system = request.form['second_system_id']

    input_items = parse_input(input_items, EVE_ITEMS_NAME_DICT)

    first_system_prices,second_system_prices = \
        get_market_information(input_items,first_system,second_system)


    return render_template('report.html',input_items=input_items, first_system_prices=first_system_prices,
                           second_system_prices=second_system_prices, EVE_ITEMS_TYPEID_DICT=EVE_ITEMS_TYPEID_DICT)

def get_items():

    holding_name_dict ={}


    for line in open(EVE_ITEMS_CSV):
        line = line.strip('\r\n')
        #TYPEID,GROUPID,TYPENAME,VOLUME
        holding_array = line.split(',')
        holding_name_dict[holding_array[2]] = {
            'TYPEID'   : holding_array[0],
            'GROUPID'     : holding_array[1],
            'VOLUME'   : holding_array[3]
        }

    return holding_name_dict

def get_market_information(input_items,first_system,second_system):
    first_url,second_url = make_url(input_items, first_system, second_system)
    first_system_prices, second_system_prices = get_prices(first_url,second_url)

    return first_system_prices,second_system_prices

def get_prices(first_url,second_url):
    first_system_prices = {}
    second_system_prices = {}

    opener = urllib.FancyURLopener({})

    first_url_data = opener.open(first_url)
    second_url_data = opener.open(second_url)

    first_root = ET.fromstring(first_url_data.read())
    second_root = ET.fromstring(second_url_data.read())

    for item in first_root.iter('type'):
        sell = item.find('sell')
        sell = sell.find('min').text


        first_system_prices[item.attrib['id']]= sell

    for item in second_root.iter('type'):
        sell = item.find('sell')
        sell = sell.find('min').text

        second_system_prices[item.attrib['id']]= sell

    return first_system_prices, second_system_prices

def make_url(input_items,first_system,second_system):
    base_url = 'http://api.eve-central.com/api/marketstat?'
    #first_url
    first_url = base_url + "usesystem=" + first_system
    for item in input_items:
        first_url = first_url + '&' + "typeid=" + item

    #second_url
    second_url = base_url + "usesystem=" + second_system
    for item in input_items:
        second_url = second_url + '&' +"typeid=" + item

    return first_url, second_url

def parse_input(raw_items, EVE_ITEMS_NAME_DICT):
    holding_items = []
    final_list = []
    raw_items = raw_items.encode('ascii', 'ignore')
    raw_items = raw_items.split('\n')

    for item in raw_items:
        item = item.strip('\r\n')
        holding_items.append(item)

    for item in holding_items:
        try:
            if EVE_ITEMS_NAME_DICT[item]:
                final_list.append(EVE_ITEMS_NAME_DICT[item]['TYPEID'])
        except KeyError:
            continue

    return sorted(final_list)

if __name__ == '__main__':
    app.run()