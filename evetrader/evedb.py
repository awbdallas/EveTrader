from config import DATABASE, EVE_ITEMS_CSV
from flask import g
from os.path import isfile
from sqlite3 import connect


def create_db():
    connection = connect(DATABASE)

    create_eveitems_table(connection)
    add_eveitems_csv_to_database(connection)

    connection.commit()
    return connection


def create_eveitems_table(connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE eveitems(
        typeid TEXT NOT NULL,
        groupid TEXT NOT NULL,
        name TEXT NOT NULL,
        volume TEXT NOT NULL)
    ''')

    connection.commit()


def add_eveitems_csv_to_database(connection):
    items = get_tuple_list_of_items()
    cursor = connection.cursor()

    cursor.executemany('INSERT INTO eveitems VALUES (?, ?, ?, ?)', items)
    connection.commit()


def get_tuple_list_of_items():
    items = []

    with open(EVE_ITEMS_CSV) as fh:
        for line in fh:
            line = line.strip()
            holding = line.split(',')

            items.append((holding[0], holding[1], holding[2], holding[3]))

    return items


def get_item_info(item):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('''SELECT typeid, groupid, name, volume
                    FROM eveitems
                    WHERE typeid = ?
                    OR name = ?
            ''', (item, item))
    result = cursor.fetchone()

    return transform_to_dict(result,
                             keys=['typeid', 'groupid', 'name', 'volume'])


def transform_to_dict(tuple_result, keys=None):
    if not tuple_result:
        return None

    holding = {}

    for result_item, result_key in zip(tuple_result, keys):
        holding[result_key] = result_item.encode('utf-8')

    return holding


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def connect_db():
    if isfile(DATABASE):
        connection = connect(DATABASE)
        return connection

    return create_db()

