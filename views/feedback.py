from flask import Blueprint, request, render_template, redirect, url_for, session, flash
import psycopg2 as db
import os


def pointChecker(s):
    if s == "0" or s == "1" or s == "2" or s == "3" or s == "4" or s == "5":
        return True
    else:
        return False


def validate_feedback(form):
    form.data = {}
    form.errors = {}
    # Type
    form_type = form.get("type", "").strip()
    if form_type == "Business Travel" or form_type == "Personal Travel":
        form.data["type"] = form_type
    else:
        form.errors["type"] = "Type must Business Travel or Personal Travel."
    # form_type
    form_class = form.get("class", "").strip()
    if form_class == "Eco" or form_class == "Business" or form_class == "Eco Plus":
        form.data["class"] = form_class
    else:
        form.errors["class"] = "Class must Eco or Business or Eco Plus."
    # satisfaction
    form_satisfaction = form.get("satisfaction", "").strip()
    if form_satisfaction == "dissatisfied" or form_satisfaction == "satisfied":
        form.data["satisfaction"] = form_class
    else:
        form.errors["satisfaction"] = "Satisfaction must satisfied or dissatisfied."
    # online support
    form_online_support = form.get("online_support", "").strip()
    if pointChecker(form_online_support) == False:
        form.errors["online_support"] = "Online support must be between 0 and 5."
    else:
        form.data["online_support"] = form_online_support
    # checking_service
    form_checking_service = form.get("checking_service", "").strip()
    if pointChecker(form_checking_service) == False:
        form.errors[
            "checking_service"
        ] = "Checking Service support must be between 0 and 5."
    else:
        form.data["checking_service"] = form_checking_service
    # baggage_handling
    form_baggage_handling = form.get("baggage_handling", "").strip()
    if pointChecker(form_baggage_handling) == False:
        form.errors["baggage_handling"] = "Baggage Handling must be between 0 and 5."
    else:
        form.data["baggage_handling"] = form_baggage_handling
    # cleanliness
    form_cleanliness = form.get("cleanliness", "").strip()
    if pointChecker(form_cleanliness) == False:
        form.errors["cleanliness"] = "Cleanliness must be between 0 and 5."
    else:
        form.data["cleanliness"] = form_cleanliness

    return len(form.errors) == 0


feedback = Blueprint("feedback", import_name=__name__, template_folder="templates")


@feedback.route("/airline_details/<ticker>", methods=["GET", "POST"])
def airline_feedback(ticker):
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute(
            "SELECT * FROM feedback WHERE airline_ticker = '{0}' order by type".format(ticker)
        )
        feedbacks = cur.fetchall()
        cur.execute("SELECT DISTINCT satisfaction FROM feedback ORDER BY satisfaction ")
        satisfaction = cur.fetchall()
        cur.close()
        return render_template(
            "feedback_airlines.html", feedbacks=feedbacks, ticker=ticker, satisfaction = satisfaction
        )
    if 'satisfaction' in request.form and request.method == "POST":
        cur.execute("SELECT DISTINCT satisfaction FROM feedback ORDER BY satisfaction ")
        satisfaction = cur.fetchall()
        satisfactionFilter = request.form["satisfaction"]
        if satisfactionFilter == "*":
            cur.execute(
            "SELECT * FROM feedback WHERE airline_ticker = '{0}'".format(ticker)
            )
        else:
            cur.execute(
            (
                "SELECT * FROM feedback WHERE satisfaction = %s and airline_ticker = %s"
            ),
            (satisfactionFilter, ticker),
            )
        feedbacks = cur.fetchall()
        if(len(feedbacks)) == 0:
            flash("No comment of exists!", "danger")
        return render_template("feedback_airlines.html", feedbacks=feedbacks, ticker=ticker, satisfaction = satisfaction)

    if request.method == "POST":
        if not "id" in session:
            flash("Please login!", "danger")
            return redirect(url_for("user_authentication.login"))
        id_feedback = request.form.getlist("feedback_id")
        for form_feedback_key in id_feedback:
            cur.execute("SELECT user_name FROM feedback WHERE id = {0}".format(form_feedback_key))
            username = cur.fetchone()
            if session["username"] != username[0]:
                flash("You can only delete your own comment", "danger")
                return redirect(url_for("feedback.airline_feedback", ticker=ticker))

        cur.execute("SELECT DISTINCT satisfaction FROM feedback ORDER BY satisfaction ")
        satisfaction = cur.fetchall()

        for form_feedback_key in id_feedback:
            cur.execute("DELETE FROM feedback WHERE id = {0}".format(form_feedback_key))
        connection.commit()
        cur.close()
        return redirect(url_for("feedback.airline_feedback", ticker=ticker, satisfaction = satisfaction))


@feedback.route("/feed_back/add/<ticker>", methods=["GET", "POST"])
def add_feedback(ticker):
    if not "id" in session:
        flash("Please login!", "danger")
        return redirect(url_for("user_authentication.login"))
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        values = {
            "type": "",
            "class": "",
            "satisfaction": "",
            "online_support": "",
            "checking_service": "",
            "baggage_handling": "",
            "cleanliness": "",
        }
        return render_template("feedback_add.html", ticker=ticker, values=values)
    if request.method == "POST":
        if not "id" in session:
            flash("Please login!", "danger")
            return redirect(url_for("user_authentication.login"))

        valid = validate_feedback(request.form)
        if not valid:
            return render_template(
                "feedback_add.html",
                ticker=ticker,
                values=request.form,
            )

        type = request.form["type"]
        classt = request.form["class"]
        satisfaction = request.form["satisfaction"]
        online_support = request.form["online_support"]
        checking_service = request.form["checking_service"]
        baggage_handling = request.form["baggage_handling"]
        cleanliness = request.form["cleanliness"]
        cur.execute(
            "INSERT INTO feedback(user_name,type,class,satisfaction,online_support,checking_service,baggage_handling,cleanliness,airline_ticker) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
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
    if not "id" in session:
        flash("Please login!", "danger")
        return redirect(url_for("user_authentication.login"))
    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM feedback WHERE id = {0}".format(id))
        feedback_info = cur.fetchall()
        id = feedback_info[0][0]
        ticker = feedback_info[0][9]
        name = ()
        name = feedback_info[0][1]
        values = {
            "type": feedback_info[0][2],
            "class": feedback_info[0][3],
            "satisfaction": feedback_info[0][4],
            "online_support": feedback_info[0][5],
            "checking_service": feedback_info[0][6],
            "baggage_handling": feedback_info[0][7],
            "cleanliness": feedback_info[0][8],
        }
        cur.close()
        return render_template(
            "feedback_update.html", id=id, ticker=ticker, values=values, name = name
        )
    if request.method == "POST":
        cur.execute("SELECT user_name FROM feedback WHERE id = {0}".format(id))

        name = cur.fetchone()
        if session["username"] != name[0]:
            flash("You can only edit your rating!", "danger")
            return redirect(url_for("feedback.airline_feedback", ticker=ticker))

        valid = validate_feedback(request.form)
        if not valid:
            return render_template(
                "feedback_update.html", id=id, ticker=ticker, values=request.form
            )

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
