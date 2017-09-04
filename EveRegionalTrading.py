from flask import Flask, render_template, request, g
from evetrader.forms.market_report import MarketForm

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'Whateveratm'


@app.route('/')
def get_input():
    return render_template('index.html')


@app.route('/market_report', methods=['GET', 'POST'])
def market_report():
    form = MarketForm()
    if request.method == 'POST' and form.validate():
        result, errors = form.handle()
        return render_template('market_report.html', errors=errors, result=result)

    return render_template('market_report.html',
                           form=form)


if __name__ == '__main__':
    app.run()
