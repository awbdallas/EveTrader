import xml.etree.ElementTree as ET
import urllib
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from contextlib import closing
from config import DEBUG, SECRET_KEY, DATABASE
from evedb import get_previous_reports, insert_new_report, connect_db, init_db
from eveitems import EveItems
from reportform import ReportForm

app = Flask(__name__)
app.config.from_object(__name__)


@app.before_request
def before_request():
    g.db = connect_db(app)


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def get_input():
    return render_template('index.html')


@app.route('/create_report', methods=['GET', 'POST'])
def add_report():
    form = ReportForm(request.form)
    if request.method == 'POST' and form.validate():
        eve_items = EveItems()

        print(form.reportname.data, form.items.data)
        insert_new_report(form.reportname.data, form.items.data)
        input_items = eve_items.get_item_info_from_typeid(form.items.data)
        first_system_prices, second_system_prices = \
            get_market_information(input_items, form.first_system_id.data,
                    form.second_system_id.data)

        return render_template('report.html', input_items=input_items,
                first_system_prices=first_system_prices,
                second_system_prices=second_system_prices)

    return render_template('create_report.html', reports=get_previous_reports(), form=form)

@app.cli.command('initdb')
def initdb_command():
    # all grabbed from http://flask.pocoo.org/docs/0.12/tutorial/dbinit/
    init_db()
    print('DB started')

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

        first_system_prices[item.attrib['id']] = {
            'SELL'  : sell_price
        }

    for item in second_root.iter('type'):
        sell = item.find('sell')
        sell_price = sell.find('min').text
        volume = sell.find('volume').text

        second_system_prices[item.attrib['id']] = {
            'VOLUME' : volume,
            'SELL'   : sell_price
        }

    return first_system_prices, second_system_prices


def make_url(input_items,first_system,second_system):
    # TODO: IIRC you're limited to 150 items for these requests
    base_url = 'http://api.eve-central.com/api/marketstat?'
    first_url = base_url + "usesystem=" + first_system
    for item in input_items:
        first_url = first_url + '&' + "typeid=" + item

    second_url = base_url + "usesystem=" + second_system
    for item in input_items:
        second_url = second_url + '&' +"typeid=" + item

    return first_url, second_url



if __name__ == '__main__':
    app.run()
