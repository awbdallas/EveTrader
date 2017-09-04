from requests import get
from config import EVE_CENTRAL_MARKETSTAT_ENDPOINT


def get_prices(items):
    urls = build_url(items)
    result = make_request(urls)
    return parse_result(result)


def build_url(items):
    url = EVE_CENTRAL_MARKETSTAT_ENDPOINT
    return url + '&'.join(['typeid=' + item for item in items]) + '&usesystem=30000142'


def make_request(urls):
    return get(urls).json()


def parse_result(result):
    result = byteify(result)
    items = []
    for item in result:
        items.append({
            'typeid': item['buy']['forQuery']['types'][0],
            'systems': item['buy']['forQuery']['systems'][0],
            'buy_max': item['buy']['max'],
            'sell_min': item['sell']['min']
        })

    return items


# Solution from stackoverflow: https://stackoverflow.com/a/13105359
def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input