from config import EVE_ITEMS_CSV
from csv import DictReader


class EveItems:
    eve_items_typeid_key = {}
    eve_items_name_key = {}

    def __init__(self):
        self.eve_items_typeid_key = self.eve_items_csv_to_dict()
        self.eve_items_name_key = self.eve_items_csv_to_dict("name")

    @staticmethod
    def eve_items_csv_to_dict(column_for_key="typeid"):
        items = {}
        with open(EVE_ITEMS_CSV) as eve_items_csv:
            for line in DictReader(eve_items_csv):
                items[line[column_for_key]] = {
                    "typeid": line["typeid"],
                    "groupid": line["groupid"],
                    "name": line["name"],
                    "volume": line["volume"]
                }

        return items

    def is_item(self, item):
        if self.eve_items_name_key.get(item, None):
            return True
        elif self.eve_items_typeid_key.get(item, None):
            return True

        return False
