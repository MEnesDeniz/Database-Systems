from flask import Blueprint, request, render_template, redirect, url_for
import psycopg2 as db
import os


flights = Blueprint('flights', import_name=__name__,
                    template_folder="templates")


@flights.route("/flights",  methods=["GET", "POST"])
def flights_page():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    cur.execute("SELECT * FROM flights")
    list_flights = cur.fetchall()
    cur.close()
    return render_template("flights_page.html", list_flights=list_flights)


@flights.route("/add_flight",  methods=["POST"])
def add_flight():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == 'POST':
        year = request.form['year']
        month = request.form['month']
        day = request.form['day']
        airline_ticker = request.form['airline_ticker']
        flight_number = request.form['flight_number']
        tail_number = request.form['tail_number']
        starting_airport = request.form['starting_airport']
        destination_airport = request.form['destination_airport']
        departure_time = request.form['departure_time']
        cur.execute("INSERT INTO flights(year,month,day,airline_ticker,flight_number,tail_number,starting_airport,destination_airport,departure_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
            year, month, day, airline_ticker, flight_number, tail_number, starting_airport, destination_airport, departure_time))
        connection.commit()
        cur.close()
        return redirect(url_for('flights.flights_page'))
