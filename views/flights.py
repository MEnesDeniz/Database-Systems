from flask import Blueprint, request, render_template, redirect, url_for
import psycopg2 as db
import os


flights = Blueprint("flights", import_name=__name__, template_folder="templates")


@flights.route("/flights", methods=["GET", "POST"])
def flights_page():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT  * FROM flights ORDER BY DATE LIMIT 100 OFFSET 0")
        list_flights = cur.fetchall()
        cur.close()
        return render_template("flights_page.html", list_flights=list_flights)


@flights.route("/flights/<airport_code>", methods=["GET", "POST"])
def airport_flights(airport_code):
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute(
            "SELECT  * FROM flights WHERE STARTING_AIRPORT = '{0}' ORDER BY DATE LIMIT 100 OFFSET 0 ".format(
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
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        return render_template("flights_add.html", airport_code=airport_code)
    if request.method == "POST":
        date = request.form["date"]
        airline_ticker = request.form["airline_ticker"]
        flight_number = request.form["flight_number"]
        tail_number = request.form["tail_number"]
        starting_airport = request.form["starting_airport"]
        destination_airport = request.form["destination_airport"]
        departure_time = request.form["dep_time"]
        arrival_time = request.form["arriv_time"]
        distance = request.form["distance"]
        cur.execute(
            "INSERT INTO flights(date,airline_ticker,flight_number,tail_number,starting_airport,destination_airport,scheduled_departure,scheduled_arrival,distance  ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                date,
                airline_ticker,
                flight_number,
                tail_number,
                starting_airport,
                destination_airport,
                departure_time,
                arrival_time,
                distance,
            ),
        )
        connection.commit()
        cur.close()
        return redirect(url_for("flights.airport_flights", airport_code=airport_code))


@flights.route("/flight_update/<airport_code>/<id>", methods=["POST", "GET"])
def update_flight(id, airport_code):
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM flights WHERE id = {0}".format(id))
        flights_info = cur.fetchall()
        cur.close()
        return render_template("flight_update.html", flights_info=flights_info)
    if request.method == "POST":
        date = request.form["date"]
        airline_ticker = request.form["airline_ticker"]
        flight_number = request.form["flight_number"]
        tail_number = request.form["tail_number"]
        starting_airport = request.form["starting_airport"]
        destination_airport = request.form["destination_airport"]
        departure_time = request.form["dep_time"]
        arrival_time = request.form["arriv_time"]
        distance = request.form["distance"]
        cur.execute(
            "UPDATE flights SET date = %s,airline_ticker = %s,flight_number =%s,tail_number =%s,starting_airport = %s,destination_airport = %s,scheduled_departure = %s,scheduled_arrival = %s,distance =%s WHERE id = %s",
            (
                date,
                airline_ticker,
                flight_number,
                tail_number,
                starting_airport,
                destination_airport,
                departure_time,
                arrival_time,
                distance,
                id,
            ),
        )
        connection.commit()
        cur.close()
        return redirect(url_for("flights.airport_flights", airport_code=airport_code))
