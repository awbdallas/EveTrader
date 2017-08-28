import xml.etree.ElementTree as ET
import urllib
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from contextlib import closing
from config import DEBUG, SECRET_KEY, DATABASE
from evetrader.evedb import get_previous_reports, insert_new_report, connect_db, init_db
from evetrader.eveitems import EveItems
from evetrader.reportform import ReportForm
from evetrader.evecentral import EveCentral

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

        insert_new_report(form.reportname.data, form.items.data)
        input_items = eve_items.get_item_info_from_typeid(form.items.data)

        first_system_prices, second_system_prices = \
            get_market_information(input_items, form.first_system_id.data,
                    form.second_system_id.data)

        print(first_system_prices, second_system_prices)

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
    evecentral = EveCentral()
    json_results = evecentral.get_price_information(input_items, [first_system, second_system])
    first_system_prices, second_system_prices = get_margins(json_results[0], json_results[1])

    return first_system_prices,second_system_prices


def get_margins(first_system_prices, second_system_prices):
    returning_first = {}
    returning = {}

    for list_item1, list_item2 in zip(first_system_prices, second_system_prices):
        item = list_item1['sell']['forQuery']['types'][0]

        first_price  = list_item1['sell']['min']
        second_price = list_item2['sell']['min']

        isk_margin = second_price - first_price
        percentage_margin = (second_price/first_price) * 100 - 100

        second_system_prices[item]['MARGIN%'] = round(percentage_margin, 2)
        second_system_prices[item]['ISKMARGIN'] = round(isk_margin, 2)

    return first_system_prices, second_system_prices


if __name__ == '__main__':
    app.run()
