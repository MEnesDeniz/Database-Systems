from flask import Blueprint, request, render_template, redirect, url_for, session
import psycopg2 as db
import os

feedback = Blueprint("feedback", import_name=__name__, template_folder="templates")


@feedback.route("/airline_details/<ticker>", methods=["GET", "POST"])
def airline_feedback(ticker):
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute(
            "SELECT * FROM feedback WHERE airline_ticker = '{0}'".format(ticker)
        )
        feedbacks = cur.fetchall()
        cur.close()
        return render_template(
            "feedback_airlines.html", feedbacks=feedbacks, ticker=ticker
        )
    else:
        id_feedback = request.form.getlist("feedback_id")
        for form_feedback_key in id_feedback:
            cur.execute("DELETE FROM feedback WHERE id = {0}".format(form_feedback_key))
        connection.commit()
        cur.close()
        return redirect(url_for("feedback.airline_feedback", ticker=ticker))


@feedback.route("/feed_back/add/<ticker>", methods=["GET", "POST"])
def add_feedback(ticker):
    if not 'id' in session:
        return redirect(url_for("user_authentication.login"))
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        return render_template("feedback_add.html", ticker=ticker)
    if request.method == "POST":
        type = request.form["type"]
        classt = request.form["class"]
        satisfaction = request.form["satisfaction"]
        online_support = request.form["online_support"]
        checking_service = request.form["checking_service"]
        baggage_handling = request.form["baggage_handling"]
        cleanliness = request.form["cleanliness"]

        cur.execute(
            "INSERT INTO feedback(nick_name,type,class,satisfaction,online_support,checking_service,baggage_handling,cleanliness,airline_ticker) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                session["username"],
                type,
                classt,
                satisfaction,
                online_support,
                checking_service,
                baggage_handling,
                cleanliness,
                ticker,
            ),
        )
        connection.commit()
        cur.close()
        return redirect(url_for("feedback.airline_feedback", ticker=ticker))


@feedback.route("/feed_back/update/<ticker>/<id>", methods=["POST", "GET"])
def update_feedback(id, ticker):
    if not 'id' in session:
        return redirect(url_for("user_authentication.login"))
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM feedback WHERE id = {0}".format(id))
        feedback_info = cur.fetchall()
        cur.close()
        return render_template("feedback_update.html", feedback_info=feedback_info)
    if request.method == "POST":
        type = request.form["type"]
        classt = request.form["class"]
        satisfaction = request.form["satisfaction"]
        online_support = request.form["online_support"]
        checking_service = request.form["checking_service"]
        baggage_handling = request.form["baggage_handling"]
        cleanliness = request.form["cleanliness"]
        cur.execute(
            "UPDATE feedback SET type = %s ,class = %s ,satisfaction = %s ,online_support = %s ,checking_service = %s ,baggage_handling = %s ,cleanliness = %s WHERE id = %s",
            (
                type,
                classt,
                satisfaction,
                online_support,
                checking_service,
                baggage_handling,
                cleanliness,
                id,
            ),
        )
        connection.commit()
        cur.close()
        return redirect(url_for("feedback.airline_feedback", ticker=ticker))
