EvE Trader
=========
Small service for creating reports for EvE regional trading


Setup
-----

This setup assumes you're in the directory for the project
```bash
virtualenv pyenv
pyenv/bin/pip install -r requirements.txt
export FLASK_APP=$(pwd)/EveRegionalTrading.py
sqlite3 /tmp/flaskr.db < schema.sql
pyenv/bin/flask run
```


TODO
----
WE'RE REDOING IT ALL BOI.

