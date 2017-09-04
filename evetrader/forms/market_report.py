from flask import g
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from evetrader.evecentral import get_prices
from evetrader.eveitems import EveItems


class MarketForm(FlaskForm):
    items = StringField('Items', validators=[DataRequired()])

    def __init__(self, **kwargs):
        FlaskForm.__init__(self, **kwargs)
        self.eveitems = EveItems()

    def handle(self):
        items, errors = self.get_valid_items()
        prices = get_prices(items)
        return prices, errors

    def get_valid_items(self):
        items = []
        errors = []

        for item in self.items.data.split(','):
            item = item.strip().encode("utf-8")

            if self.eveitems.is_item(item):
                items.append(item)
            else:
                errors.append('Invalid item: %s' % item)

        return items, errors