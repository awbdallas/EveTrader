from requests import get
from config import EVE_CENTRAL_MARKETSTAT_ENDPOINT


class EveCentral:

    def __init__(self):
        pass

    def get_price_information(self, list_of_items, systems):
        print(list_of_items)
        urls = []
        for system in systems:
            urls.append(self.build_url(list_of_items, system))

        print(urls)
        results = []
        for url in urls:
            results.append(self.make_request(url))

        print(results)
        return results

    @staticmethod
    def build_url(list_of_items, system):
        base_url = EVE_CENTRAL_MARKETSTAT_ENDPOINT +\
                '&'.join(['typeid=' + typeid for typeid in list_of_items])
        base_url += '&usesystem=' + system

        return base_url

    @staticmethod
    def make_request(url):
        result = get(url)

        if result.status_code == 200:
            return result.json()
