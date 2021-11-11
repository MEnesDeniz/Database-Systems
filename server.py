from flask import Flask, redirect, url_for, render_template
import os
from dbinit import initialize



app = Flask(__name__)

HEROKU_LAUNCH = False

if(not HEROKU_LAUNCH):
    os.environ['DATABASE_URL'] = "dbname = 'postgres' user='postgres' host='localhost' password='123'"
    initialize(os.environ.get('DATABASE_URL'))


@app.route("/")
def home_page():
    return render_template("home_page.html")

@app.route("/airlines")
def airlines_page():
    return render_template("airlines_page.html")

@app.route("/airports")
def airports_page():
    return render_template("airports_page.html")

@app.route("/flights")
def flights_page():
    return render_template("flights_page.html")


if __name__ == "__main__":
    if(not HEROKU_LAUNCH):
        app.run(debug = False)
    else:
        app.run(debug = True)
