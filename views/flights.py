from flask import Blueprint, request, render_template, redirect, url_for
import psycopg2 as db
import os


flights = Blueprint('flights', import_name=__name__,
                    template_folder="templates")


@flights.route("/flights",  methods=["GET", "POST"])
def flights_page():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT  * FROM flights ORDER BY DATE LIMIT 100")
        list_flights = cur.fetchall()
        cur.close()
        return render_template("flights_page.html", list_flights=list_flights)
    else:
        flight_keys = request.form.getlist("flight_keys")
        for form_flight_keys in flight_keys:
            cur.execute('DELETE FROM flights WHERE id = {0}'.format(form_flight_keys))
        connection.commit()
        cur.close()
        return redirect(url_for('flights.flights_page'))


@flights.route("/add_flight",  methods=["POST"])
def add_flight():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == 'POST':
        date = request.form['date']
        airline_ticker = request.form['airline_ticker']
        flight_number = request.form['flight_number']
        tail_number = request.form['tail_number']
        starting_airport = request.form['starting_airport']
        destination_airport = request.form['destination_airport']
        departure_time = request.form['dep_time']
        arrival_time = request.form['arriv_time']
        distance = request.form['distance']
        cur.execute("INSERT INTO flights(date,airline_ticker,flight_number,tail_number,starting_airport,destination_airport,scheduled_departure,scheduled_arrival,distance  ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
            date, airline_ticker, flight_number, tail_number, starting_airport, destination_airport, departure_time, arrival_time, distance))
        connection.commit()
        cur.close()
        return redirect(url_for('flights.flights_page'))
