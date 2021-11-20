from flask import Flask, redirect, url_for, render_template, Blueprint
import os
from dbinit import initialize


from views.airlines import airlines
from views.flights import flights
from views.airports import airports

app = Flask(__name__)

app.register_blueprint(airports)
app.register_blueprint(airlines)
app.register_blueprint(flights)

HEROKU_LAUNCH = False

if(not HEROKU_LAUNCH):
    os.environ['DATABASE_URL'] = "dbname = 'postgres' user='postgres' host='localhost' password='123'"
    initialize(os.environ.get('DATABASE_URL'))


@app.route("/")
def home_page():
    return render_template("home_page.html")


if __name__ == "__main__":
    if(not HEROKU_LAUNCH):
        app.run(debug=False)
    else:
        app.run(debug=True)
