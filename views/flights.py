from flask import Blueprint, request, render_template, redirect, url_for,session
import psycopg2 as db
import math
import os

def createList(r1, r2):
  
    # Testing if range r1 and r2 
    # are equal
    if (r1 == r2):
        return r1
  
    else:
  
        # Create empty list
        res = []
  
        # loop to append successors to 
        # list until r2 is reached.
        while(r1 < r2+1 ):
              
            res.append(r1)
            r1 += 1
        return res

def validate_flight(form):
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

    

flights = Blueprint("flights", import_name=__name__, template_folder="templates")


@flights.route("/flights/page", defaults={"current_page": 1})
@flights.route("/flights/page/<int:current_page>", methods=["GET", "POST"])
def flights_page(current_page):
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT DISTINCT airport_code FROM airports ORDER BY airport_code ")
        all_destinations = cur.fetchall()
        cur.close()

        cur = connection.cursor()
        per_page = 50
        cur.execute("SELECT count(*) FROM FLIGHTS")
        total = cur.fetchone()[0]
        cur.close()

        page_count = math.ceil(total / per_page)
        offset = per_page * (current_page - 1)
        if page_count > 1:
            cur = connection.cursor()
            cur.execute(
                "SELECT * FROM flights order by DATE, airline_ticker desc LIMIT {} OFFSET {}".format(
                    per_page, offset
                )
            )
            cur.close()
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
            r1 = 1
            r2 = 5
            page_list = createList(r1,r2)
            cur = connection.cursor()
            cur.execute("SELECT * FROM flights")

        list_flights = cur.fetchall()
        cur.close()
        return render_template("flights_page.html", list_flights=list_flights ,current_page = page_list, all_destinations = all_destinations)


@flights.route("/flights/filtered", methods=["POST"])
def filtered_flight():
    current_page = 1
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "POST":
        cur.execute("SELECT DISTINCT airport_code FROM airports ORDER BY airport_code ")
        all_destinations = cur.fetchone()

        dateS = request.form["date"]
        startAirport = request.form["starting_airport"]
        endAirport = request.form["destination_airport"]
        cur.execute(
            "(SELECT  * FROM flights WHERE date = %s and starting_aiport = %s and destination", (dateS,startAirport,endAirport))
        starting_ones = cur.fetchone()
        cur.close()
    return render_template("flights_page.html", starting_ones=starting_ones ,current_page = current_page, all_destinations=all_destinations)














@flights.route("/flights/<airport_code>", methods=["GET", "POST"])
def airport_flights(airport_code):
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute(
            "SELECT  * FROM flights WHERE STARTING_AIRPORT = '{0}' ORDER BY DATE DESC ".format(
                airport_code
            )
        )
        flight_list = cur.fetchall()
        cur.close()
        return render_template(
            "flights_by_airport.html",
            flight_list=flight_list,
            airport_code=airport_code,
        )
    else:
        flight_keys = request.form.getlist("flight_keys")
        for form_flight_keys in flight_keys:
            cur.execute("DELETE FROM flights WHERE id = {0}".format(form_flight_keys))
        connection.commit()
        cur.close()
        return redirect(url_for("flights.airport_flights", airport_code=airport_code))


@flights.route("/add_flight/<airport_code>", methods=["POST", "GET"])
def add_flight(airport_code):
    if not 'id' in session:
        return redirect(url_for("user_authentication.login"))
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT DISTINCT airport_code FROM airports")
        all_destinations = cur.fetchall()
        cur.execute("SELECT DISTINCT ticker FROM airlines")
        all_tickers = cur.fetchall()
        cur.close()
        return render_template("flights_add.html", airport_code=airport_code, all_destinations = all_destinations, all_tickers = all_tickers)
    if request.method == "POST":
        date = request.form["date"]
        airline_ticker = request.form["airline_ticker"]
        flight_number = request.form["flight_number"]
        tail_number = request.form["tail_number"]
        destination_airport = request.form["destination_airport"]
        departure_time = request.form["dep_time"]
        arrival_time = request.form["arriv_time"]
        cur.execute(
            "INSERT INTO flights(date,airline_ticker,flight_number,tail_number,starting_airport,destination_airport,scheduled_departure,scheduled_arrival  ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                date,
                airline_ticker,
                flight_number,
                tail_number,
                airport_code,
                destination_airport,
                departure_time,
                arrival_time,
            ),
        )
        connection.commit()
        cur.close()
        return redirect(url_for("flights.airport_flights", airport_code=airport_code))


@flights.route("/flight_update/<airport_code>/<id>", methods=["POST", "GET"])
def update_flight(id, airport_code):
    if not 'id' in session:
        return redirect(url_for("user_authentication.login"))
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM flights WHERE id = {0}".format(id))
        flights_info = cur.fetchall()
        cur.execute("SELECT DISTINCT airport_code FROM airports")
        all_destinations = cur.fetchall()
        cur.execute("SELECT DISTINCT ticker FROM airlines")
        all_tickers = cur.fetchall()
        cur.close()
        return render_template("flights_update.html", flights_info=flights_info , all_destinations = all_destinations, all_tickers = all_tickers)
    if request.method == "POST":
        date = request.form["date"]
        airline_ticker = request.form["airline_ticker"]
        flight_number = request.form["flight_number"]
        tail_number = request.form["tail_number"]
        destination_airport = request.form["destination_airport"]
        departure_time = request.form["dep_time"]
        arrival_time = request.form["arriv_time"]
        cur.execute(
            "UPDATE flights SET date = %s,airline_ticker = %s,flight_number =%s,tail_number =%s,starting_airport = %s,destination_airport = %s,scheduled_departure = %s,scheduled_arrival = %s WHERE id = %s",
            (
                date,
                airline_ticker,
                flight_number,
                tail_number,
                airport_code,
                destination_airport,
                departure_time,
                arrival_time,
                id,
            ),
        )
        connection.commit()
        cur.close()
        return redirect(url_for("flights.airport_flights", airport_code=airport_code))
