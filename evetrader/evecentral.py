from requests import get
from config import EVE_CENTRAL_MARKETSTAT_ENDPOINT


def get_prices(items):
    urls = build_url(items)
    result = make_request(urls)
    return parse_result(result, items)


def build_url(items):
    url = EVE_CENTRAL_MARKETSTAT_ENDPOINT
    # TODO: Actually support other systems
    return url + '&'.join(['typeid=' + item['typeid'] for item in items])\
        + '&usesystem=30000142'


def make_request(urls):
    # TODO support multiple urls like it's supposed to
    return byteify(get(urls).json())


def parse_result(result, items):
    for item, resultitem in zip(items, result):
        item['systems'] = resultitem['buy']['forQuery']['systems'][0]
        item['buy_max'] = resultitem['buy']['max']
        item['sell_min'] = resultitem['sell']['min']

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
