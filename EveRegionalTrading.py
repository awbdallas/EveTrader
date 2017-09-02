from flask import Flask, g, render_template

app = Flask(__name__)
app.config.from_object(__name__)


@app.before_request
def before_request():
    pass


@app.teardown_request
def teardown_request(exception):
    pass


@app.route('/')
def get_input():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
