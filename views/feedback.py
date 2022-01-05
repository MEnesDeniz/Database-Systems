from flask import Blueprint, request, render_template, redirect, url_for, session
import psycopg2 as db
import os

feedback = Blueprint('feedback', import_name=__name__,
                     template_folder="templates")


@feedback.route("/airline_details/<ticker>",  methods=["GET", "POST"])
def airline_feedback(ticker):
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute(
            "SELECT * FROM feedback WHERE airline_ticker = '{0}'".format(ticker))
        feedbacks = cur.fetchall()
        cur.close()
        return render_template("airline_feedback.html", feedbacks=feedbacks)
    else:
        id_feedback = request.form.getlist("feedback_id")
        for form_feedback_key in id_feedback:
            cur.execute(
                'DELETE FROM feedback WHERE id = {0}'.format(form_feedback_key))
        connection.commit()
        cur.close()
        return redirect(url_for('feedback.airline_feedback', ticker= ticker))

@feedback.route("/airline_details/<ticker>/add",  methods=["POST"])
def add_feedback():
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == 'POST':
        airline_ticker = request.form['airline_ticker']
        airline_name = request.form['airline_name']
        cur.execute("INSERT INTO airlines(ticker,name) VALUES (%s,%s)",
                    (airline_ticker, airline_name))
        connection.commit()
        cur.close()
        return redirect(url_for('airlines.airlines_page'))

