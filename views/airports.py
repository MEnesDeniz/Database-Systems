from flask import Blueprint, request, render_template, redirect, url_for, session
import math
import psycopg2 as db
import os


def validate_airports_form(form):
    form.data = {}
    form.errors = {}
    # Airport_Code
    form_airport_code = form.get("airport_code").strip()
    if len(form_airport_code) != 3:
        form.errors["airport_code"] = "Airport code must be 3 character."
    else:
        form.data["airport_code"] = form_airport_code
    # Airport_Name
    form_airport_name = form.get("airport_name", "").strip()
    if len(form_airport_name) == 0:
        form.errors["airport_name"] = "Airport name can not be left blank."
    else:
        form.data["airport_name"] = form_airport_name
    # City
    form_city = form.get("city", "").strip()
    if len(form_city) == 0:
        form.errors["city"] = "City can not be left blank."
    elif len(form_city) >= 33:
        form.errors["city"] = "City can not be higher 32 characters."
    else:
        form.data["city"] = form_city
    # State
    form_state = form.get("state", "").strip()
    if len(form_state) != 2:
        form.errors["state"] = "State must be 2 character."
    else:
        form.data["state"] = form_state
    # Country
    form_country = form.get("country", "").strip()
    if len(form_country) == 0:
        form.errors["country"] = "Country can not be left blank."
    else:
        form.data["country"] = form_country
    # Latitude
    form_latitude = form.get("latitude").strip("-")
    x = form_latitude.replace(".", "", 1).isdigit()
    if not form_latitude:
        form.data["latitude"] = None
    elif x == False:
        form.errors["latitude"] = "Latitude must be float."
    else:
        form.data["latitude"] = form_latitude
    # Longtitude
    form_longitude = form.get("longitude").strip("-")
    y = form_longitude.replace(".", "", 1).isdigit()
    if not form_longitude:
        form.data["latitude"] = None
    elif y == False:
        form.errors["longitude"] = "Longitude must be float."
    else:
        form.data["longitude"] = form_longitude
    return len(form.errors) == 0


airports = Blueprint("airports", import_name=__name__, template_folder="templates")


@airports.route("/airports/page", defaults={"current_page": 1})
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
                "SELECT * FROM airports order by airport_code LIMIT {} OFFSET {}".format(
                    per_page, offset
                )
            )
            if current_page == 1:
                page_list = (
                    current_page,
                    current_page + 1,
                    current_page + 2,
                    page_count,
                )
            elif 1 < current_page < page_count - 1:
                page_list = (
                    current_page - 1,
                    current_page,
                    current_page + 1,
                    page_count,
                )
            elif current_page == page_count - 1:
                page_list = (
                    current_page - 3,
                    current_page - 2,
                    current_page - 1,
                    page_count,
                )
            elif current_page == page_count:
                page_list = (
                    current_page - 3,
                    current_page - 2,
                    current_page - 1,
                    current_page,
                )
        else:
            cur.execute("SELECT * FROM airports")
        list_airports = cur.fetchall()
        cur.close()
        return render_template(
            "airports_page.html", list_airports=list_airports, current_page=page_list
        )


@airports.route("/del_airport", methods=["POST", "GET"])
def del_airport():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "POST":
        airport_keys = request.form.getlist("airport_keys")
        for form_airport_key in airport_keys:
            cur.execute("DELETE FROM airports WHERE id = {0}".format(form_airport_key))
        connection.commit()
        cur.close()
        return redirect(url_for("airports.airports_page"))


@airports.route("/add_airport", methods=["POST", "GET"])
def add_airport():
    if not "id" in session:
        return redirect(url_for("user_authentication.login"))

    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        values = {
            "airport_code": "",
            "airport_name": "",
            "city": "",
            "state": "",
            "country": "",
            "latitude": "",
            "longitude": "",
        }
        return render_template("airports_add.html", values=values)
    if request.method == "POST":
        valid = validate_airports_form(request.form)
        if not valid:
            return render_template(
                "airports_add.html",
                values=request.form,
            )
        airport_code = request.form.data["airport_code"]
        airport_name = request.form.data["airport_name"]
        city = request.form.data["city"]
        state = request.form.data["state"]
        country = request.form.data["country"]
        latitude = request.form.data["latitude"]
        longitude = request.form.data["longitude"]
        cur.execute(
            "INSERT INTO airports(airport_code,airport_name,city,state,country,latitude,longitude) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (airport_code, airport_name, city, state, country, latitude, longitude),
        )
        connection.commit()
        cur.close()
        return redirect(url_for("airports.airports_page"))


@airports.route("/airport_update/<id>", methods=["POST", "GET"])
def update_airport(id):
    if not "id" in session:
        return redirect(url_for("user_authentication.login"))
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM airports WHERE id = {0}".format(id))
        airports_infos = cur.fetchall()
        Aid = airports_infos[0][0]
        values = {
            "airport_code": airports_infos[0][1],
            "airport_name": airports_infos[0][2],
            "city": airports_infos[0][3],
            "state": airports_infos[0][4],
            "country": airports_infos[0][5],
            "latitude": airports_infos[0][6],
            "longitude": airports_infos[0][7],
        }
        cur.close()
        return render_template("airports_update.html", id = Aid, values=values)
    if request.method == "POST":
        valid = validate_airports_form(request.form)
        if not valid:
            return render_template(
                "airports_update.html",
                values=request.form,
                id = id
            )
        airport_code = request.form.data["airport_code"]
        airport_name = request.form.data["airport_name"]
        city = request.form.data["city"]
        state = request.form.data["state"]
        country = request.form.data["country"]
        latitude = request.form.data["latitude"]
        longitude = request.form.data["longitude"]
        cur.execute(
            "UPDATE airports SET airport_code = %s ,airport_name = %s ,city = %s ,state = %s ,country = %s ,latitude = %s ,longitude = %s WHERE id = %s",
            (airport_code, airport_name, city, state, country, latitude, longitude, id),
        )
        connection.commit()
        cur.close()
        return redirect(url_for("airports.airports_page"))
