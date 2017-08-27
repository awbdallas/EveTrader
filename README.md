EvE Trader
=========
Small service to help with eve trading. Not that good tho :/ 


Setup
-----
virtualenv pyenv
pyenv/bin/pip install -r requirements.txt
export FLASK_APP=$(pwd)/EveRegionalTrading.py
sqlite3 /tmp/flaskr.db < schema.sql
pyenv/bin/flask run


TODO
----
Setup Instructions
Refactor some of the code so that it's nice
May switch the endpoints to something that's not....awful
