from flask import Blueprint, request, render_template, redirect, url_for, session, flash
import psycopg2 as db
import math
import os
from dateutil import parser

from views.airports import validate_airports_form


def validate_flight(form,all_destinations):
    form.data = {}
    form.errors = {}

    # Date
    form_date = form.get("date")
    if bool(parser.parse(form_date)):
        form.data["date"] = form_date
    else:
        form.errors["date"] = "Date Format is YYYY-MM-DD."
    # airline_ticker
    form_airline_ticker = form.get("airline_ticker", "").strip()
    if len(form_airline_ticker) == 0:
        form.errors["airline_ticker"] = "Airline Ticker can not be left blank."
    else:
        form.data["airline_ticker"] = form_airline_ticker
    # flight_number
    form_flight_number = form.get("flight_number").strip()
    if len(form_flight_number) == 0:
        form.errors["flight_number"] = "Flight number can not be left blank."
    else:
        form.data["flight_number"] = form_flight_number
    # tail_number
    form_tail_number = form.get("tail_number").strip()
    if len(form_tail_number) != 6:
        form.errors["tail_number"] = "Tail number must be 6 character."
    else:
        form.data["tail_number"] = form_tail_number
    # Destination Airport
    form_destination_airport = form.get("destination_airport", "").strip()
    res = False

    for a in all_destinations:
        if form_destination_airport == a[0]:
            res = True

    if res == True:
        form.data["destination_airport"] = form_destination_airport
    else:
        form.errors[
            "destination_airport"
        ] = "Destination airport must be existing airport."
    # Departure Time
    form_dep_time = form.get("dep_time").split(":")
    if (
        len(form_dep_time[0]) != 2
        or form_dep_time[0] < "00"
        or form_dep_time[0] > "23"
        or len(form_dep_time[1]) != 2
        or form_dep_time[1] < "00"
        or form_dep_time[1] > "59"
    ):
        form.errors["dep_time"] = "Departure time  must be between valid times."
    else:
        form_dep_time = form.get("dep_time")
        form.data["dep_time"] = form_dep_time
    # Arrival Time
    form_arriv_time = form.get("arriv_time").split(":")
    if (
        len(form_arriv_time[0]) != 2
        or form_arriv_time[0] < "00"
        or form_arriv_time[0] > "23"
        or len(form_arriv_time[1]) != 2
        or form_arriv_time[1] < "00"
        or form_arriv_time[1] > "59"
    ):
        form.errors["arriv_time"] = "Arrival time must be between valid times."
    else:
        form_arriv_time = form.get("arriv_time")
        form.data["arriv_time"] = form_arriv_time

    return len(form.errors) == 0


flights = Blueprint("flights", import_name=__name__, template_folder="templates")


@flights.route("/flights", methods=["GET", "POST"])
def flights_page():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT DISTINCT airport_code FROM airports ORDER BY airport_code ")
        all_destinations = cur.fetchall()
        list_flights = ()
        cur.close()
        return render_template(
            "flights_page.html",
            list_flights=list_flights,
            all_destinations=all_destinations,
        )
    if request.method == "POST":
        cur.execute("SELECT DISTINCT airport_code FROM airports ORDER BY airport_code ")
        all_destinations = cur.fetchall()

        if request.form["date"]:
            dateS = request.form["date"]

        if request.form["starting_airport"]:
            startAirport = request.form["starting_airport"]

        if request.form["starting_airport"]:
            endAirport = request.form["destination_airport"]

        cur.execute(
            (
                "SELECT * FROM flights WHERE date = %s and starting_airport = %s and destination_airport = %s"
            ),
            (dateS, startAirport, endAirport),
        )
        list_flights = cur.fetchall()
        if len(list_flights) == 0:
            flash("There exists not a flight like this!", "danger")

        return render_template(
            "flights_page.html",
            list_flights=list_flights,
            all_destinations=all_destinations,
        )


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
        if session["isAdmin"] == False:
            flash("Only admins have operate on this", "danger")
            return redirect(url_for("flights.airport_flights", airport_code=airport_code))
        flight_keys = request.form.getlist("flight_keys")
        for form_flight_keys in flight_keys:
            cur.execute("DELETE FROM flights WHERE id = {0}".format(form_flight_keys))
        connection.commit()
        cur.close()
        return redirect(url_for("flights.airport_flights", airport_code=airport_code))


@flights.route("/add_flight/<airport_code>", methods=["POST", "GET"])
def add_flight(airport_code):
    if session["isAdmin"] == False:
        flash("Only admins have operate on this", "danger")
        return redirect(url_for("flights.airport_flights", airport_code=airport_code))
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        values = {
            "date": "",
            "airline_ticker": "",
            "flight_number": "",
            "tail_number": "",
            "destination_airport": "",
            "scheduled_departure": "",
            "scheduled_arrival": "",
        }
        cur.execute("SELECT DISTINCT airport_code FROM airports")
        all_destinations = cur.fetchall()
        cur.execute("SELECT DISTINCT ticker FROM airlines")
        all_tickers = cur.fetchall()
        cur.close()
        return render_template(
            "flights_add.html",
            airport_code=airport_code,
            all_destinations=all_destinations,
            all_tickers=all_tickers,
            values=values,
        )
    if request.method == "POST":
        if session["isAdmin"] == False:
            flash("Only admins have operate on this", "danger")
            return redirect(url_for("flights.airport_flights", airport_code=airport_code))
        cur.execute("SELECT DISTINCT airport_code FROM airports")
        all_destinations = cur.fetchall()
        cur.execute("SELECT DISTINCT ticker FROM airlines")
        all_tickers = cur.fetchall()

        valid = validate_flight(request.form,all_destinations)

        if not valid:
            return render_template(
                "flights_add.html",
                airport_code=airport_code,
                all_destinations=all_destinations,
                all_tickers=all_tickers,
                values=request.form,
            )
        date = request.form.data["date"]
        airline_ticker = request.form.data["airline_ticker"]
        flight_number = request.form.data["flight_number"]
        tail_number = request.form.data["tail_number"]
        destination_airport = request.form.data["destination_airport"]
        departure_time = request.form.data["dep_time"]
        arrival_time = request.form.data["arriv_time"]
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
    if session["isAdmin"] == False:
        flash("Only admins have operate on this", "danger")
        return redirect(url_for("flights.airport_flights", airport_code=airport_code))

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
        values = {
            "date": flights_info[0][1],
            "airline_ticker": flights_info[0][2],
            "flight_number": flights_info[0][3],
            "tail_number": flights_info[0][4],
            "destination_airport": flights_info[0][6],
            "scheduled_departure": flights_info[0][7],
            "scheduled_arrival": flights_info[0][8],
        }
        return render_template(
            "flights_update.html",
            values=values,
            all_destinations=all_destinations,
            all_tickers=all_tickers,
            airport_code=airport_code,
            id = id,
        )

    if request.method == "POST":
        if session["isAdmin"] == False:
            flash("Only admins have operate on this", "danger")
            return redirect(url_for("flights.airport_flights", airport_code=airport_code))

        cur.execute("SELECT DISTINCT airport_code FROM airports")
        all_destinations = cur.fetchall()
        cur.execute("SELECT DISTINCT ticker FROM airlines")
        all_tickers = cur.fetchall()
        valid = validate_flight(request.form,all_destinations)

        if not valid:
            return render_template(
                "flights_update.html",
                airport_code=airport_code,
                all_destinations=all_destinations,
                all_tickers=all_tickers,
                values=request.form,
                id = id
            )

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
