from flask import Blueprint, request, render_template, redirect, url_for
import math
import psycopg2 as db
import os


airports = Blueprint('airports', import_name=__name__,
                     template_folder="templates")


@airports.route("/airports", defaults={"current_page": 1})
@airports.route("/airports/page/<int:current_page>", methods=["GET", "POST"])
def airports_page(current_page):
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        per_page = 25
        cur.execute("select count(*) from airports")
        total = cur.fetchone()[0]
        page_count = math.ceil(total / per_page)
        offset = per_page * (current_page - 1)
        if page_count > 1:
            cur.execute(
                "SELECT * FROM airports order by airport_code LIMIT {} OFFSET {}".format(per_page, offset))
            if current_page == 1:
                page_list = (current_page, current_page +
                             1, current_page+2, page_count)
            elif 1 < current_page < page_count:
                page_list = (current_page-1, current_page,
                             current_page+1, page_count)
            elif current_page == page_count:
                page_list = (current_page-3, current_page -
                             2, current_page-1, current_page)
        else:
            cur.execute("SELECT * FROM airports")
        list_airports = cur.fetchall()
        cur.close()
        return render_template("airports_page.html", list_airports=list_airports, current_page=page_list)
    else:
        airport_keys = request.form.getlist("airport_keys")
        for form_airport_key in airport_keys:
            cur.execute(
                'DELETE FROM airports WHERE id = {0}'.format(form_airport_key))
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


@airports.route("/airport_update/<id>", methods=['POST', 'GET'])
def update_airport(id):
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == 'GET':
        cur.execute('SELECT * FROM airports WHERE id = {0}'. format(id))
        airports_info = cur.fetchall()
        cur.close()
    if request.method == 'POST':
        airport_code = request.form['airport_code']
        airport_name = request.form['airport_name']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        cur.execute("UPDATE airports SET airport_code = %s ,airport_name = %s ,city = %s ,state = %s ,country = %s ,latitude = %s ,longitude = %s WHERE id = %s", (
            airport_code, airport_name, city, state, country, latitude, longitude, id))
        connection.commit()
        cur.close()
        return redirect(url_for('airports.airports_page'))
    return render_template("airports_update.html", airports_info=airports_info)
