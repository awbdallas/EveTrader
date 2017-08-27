import sqlite3

from flask import g


def connect_db(app):
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_previous_reports():
    cur = g.db.execute('select title, text from reports order by id desc')
    reports = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]


def insert_new_report(title, text):
    g.db.execute('insert into reports (title, text) values (?, ?)',
                 [title, text.replace('\n', '<br />')])
    g.db.commit()


def init_db():
    with app.open_resource('schema.sql', mode='r') as f:
        g.db.cursor().executescript(f.read())
    g.db.commit()
