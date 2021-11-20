from flask import Blueprint, request, render_template, redirect, url_for
import psycopg2 as db
import os


airports = Blueprint('airports', import_name=__name__,
                     template_folder="templates")


@airports.route("/airports",  methods=["GET", "POST"])
def airports_page():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM airports")
        list_airports = cur.fetchall()
        cur.close()
        return render_template("airports_page.html", list_airports=list_airports)
    else:
        airport_keys = request.form.getlist("airport_keys")
        for form_airport_key in airport_keys:
            cur.execute('DELETE FROM airports WHERE id = {0}'.format(form_airport_key))
        connection.commit()
        cur.close()
        return redirect(url_for('airports.airports_page'))


@airports.route("/add_airport",  methods=["POST"])
def add_airport():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == 'POST':
        airport_code = request.form['airport_code']
        airport_name = request.form['airport_name']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        cur.execute("INSERT INTO airports(airport_code,airport_name,city,state,country,latitude,longitude) VALUES (%s,%s,%s,%s,%s,%s,%s)", (
            airport_code, airport_name, city, state, country, latitude, longitude))
        connection.commit()
        cur.close()
        return redirect(url_for('airports.airports_page'))
