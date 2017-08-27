from config import EVE_ITEMS_CSV


class EveItems:
    eve_name_dict = None
    eve_typeid_dict = None


    def __init__(self):
        self.eve_name_dict = {}
        self.eve_typeid_dict = {}
        self.populate_name_dict()
        self.populate_typeid_dict()


    def populate_name_dict(self):
        for line in open(EVE_ITEMS_CSV):
            line = line.strip('\r\n')
            holding_array = line.split(',')
            self.eve_name_dict[holding_array[2]] = {
                'TYPEID'  : holding_array[0],
                'GROUPID' : holding_array[1],
                'VOLUME'  : holding_array[3]
            }


    def populate_typeid_dict(self):
        for line in open(EVE_ITEMS_CSV):
            line = line.strip('\r\n')
            holding_array = line.split(',')
            self.eve_typeid_dict[holding_array[0]] = {
                'TYPENAME' : holding_array[2],
                'GROUPID'  : holding_array[1],
                'VOLUME'   : holding_array[3]
            }


    def get_item_info_from_typeid(self, raw_items):
        holding_items = []
        final_list = []

        for item in raw_items:
            item = item.strip('\r\n')
            holding_items.append(item)

        holding_items = sorted(holding_items)
        for item in holding_items:
            try:
                if self.eve_name_dict[item]:
                    final_list.append(self.eve_name_dict[item]['TYPEID'])
            except KeyError:
                continue

        return final_list
