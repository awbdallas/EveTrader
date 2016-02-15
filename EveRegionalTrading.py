import xml.etree.ElementTree as ET
import urllib
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from contextlib import closing

#config
DEBUG      = True
SECRET_KEY = 'development key'
DATABASE = '/tmp/flaskr.db'

#For the actual program
EVE_ITEMS_CSV = './eve_items/eve_items.csv'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def get_input():
    cur = g.db.execute('select title, text from reports order by id desc')
    reports = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('index.html', reports=reports)

@app.route('/report',methods=['POST'])
def add_query():
    eve_items_typeid_dict, eve_items_name_dict = get_items()

    report_title  = request.form['report_name']
    input_items   = request.form['items_text']
    first_system  = request.form['first_system_id']
    second_system = request.form['second_system_id']

    g.db.execute('insert into reports (title, text) values (?, ?)',
                 [report_title, input_items.replace('\n', '<br />')])
    g.db.commit()

    input_items = parse_input(input_items, eve_items_name_dict)

    first_system_prices,second_system_prices = \
        get_market_information(input_items,first_system,second_system)


    return render_template('report.html',input_items=input_items, first_system_prices=first_system_prices,
                           second_system_prices=second_system_prices, eve_items_typeid_dict=eve_items_typeid_dict)

def get_items():

    holding_name_dict = {}
    holding_typeid_dict = {}

    for line in open(EVE_ITEMS_CSV):
        line = line.strip('\r\n')
        #TYPEID,GROUPID,TYPENAME,VOLUME
        holding_array = line.split(',')
        holding_name_dict[holding_array[2]] = {
            'TYPEID'  : holding_array[0],
            'GROUPID' : holding_array[1],
            'VOLUME'  : holding_array[3]
        }

    for line in open(EVE_ITEMS_CSV):
        line = line.strip('\r\n')
        #TYPEID,GROUPID,TYPENAME,VOLUME
        holding_array = line.split(',')
        holding_typeid_dict[holding_array[0]] = {
            'TYPENAME' : holding_array[2],
            'GROUPID'  : holding_array[1],
            'VOLUME'   : holding_array[3]
        }

    return holding_typeid_dict, holding_name_dict

def get_market_information(input_items,first_system,second_system):
    first_url,second_url = make_url(input_items, first_system, second_system)
    first_system_prices, second_system_prices = get_prices(first_url,second_url)

    first_system_prices, second_system_prices = get_margins(first_system_prices, second_system_prices)

    return first_system_prices,second_system_prices

def get_margins(first_system_prices, second_system_prices):
    for key in first_system_prices.keys():
        first_price  = float(first_system_prices[key]['SELL'])
        second_price = float(second_system_prices[key]['SELL'])

        isk_margin = second_price - first_price
        percentage_margin = (second_price/first_price) * 100 - 100

        second_system_prices[key]['MARGIN%'] = round(percentage_margin, 2)
        second_system_prices[key]['ISKMARGIN'] = round(isk_margin, 2)

    return first_system_prices, second_system_prices

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
        sell_price = sell.find('min').text

        #first_system_prices[item.attrib['id']] = {}
        first_system_prices[item.attrib['id']] = {
            'SELL'  : sell_price
        }

    for item in second_root.iter('type'):
        sell = item.find('sell')
        sell_price = sell.find('min').text
        volume = sell.find('volume').text

        #second_system_prices[item.attrib['id']] = {}
        second_system_prices[item.attrib['id']] = {
            'VOLUME' : volume,
            'SELL'   : sell_price
        }

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

def parse_input(raw_items, eve_items_name_dict):
    holding_items = []
    final_list = []
    raw_items = raw_items.encode('ascii', 'ignore')
    raw_items = raw_items.split('\n')

    for item in raw_items:
        item = item.strip('\r\n')
        holding_items.append(item)

    holding_items = sorted(holding_items)
    for item in holding_items:
        try:
            if eve_items_name_dict[item]:
                final_list.append(eve_items_name_dict[item]['TYPEID'])
        except KeyError:
            continue

    return final_list

if __name__ == '__main__':
    app.run()