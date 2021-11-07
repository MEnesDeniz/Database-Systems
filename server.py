from flask import Flask, redirect, url_for, render_template
import os
from dbinit import initialize
from psycopg2 import extensions


extensions.register_type(extensions.UNICODE)
extensions.register_type(extensions.UNICODEARRAY)


app = Flask(__name__)

HEROKU_LAUNCH = False

if(not HEROKU_LAUNCH):
    os.environ['DATABASE_URL'] = "dbname = 'postgres' user='postgres' host='localhost' password='123' "
    initialize(os.environ.get('DATABASE_URL'))


@app.route("/")
def home_page():
    return render_template("home_page.html", id = 100)


if __name__ == "__main__":
    if(not HEROKU_LAUNCH):
        app.run(debug = False)
    else:
        app.run(debug = True)
