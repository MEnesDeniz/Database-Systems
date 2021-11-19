from flask import Blueprint, request, render_template
import psycopg2 as db
import os

airlines = Blueprint('airlines',import_name=__name__,template_folder="templates")

@airlines.route("/airlines",  methods=["GET", "POST"])
def airlines_page():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    cur.execute("SELECT * FROM airlines")
    list_airlines = cur.fetchall()
    cur.close()
    return render_template("airlines_page.html", list_airlines = list_airlines)