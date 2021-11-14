from flask import Blueprint, request, render_template

flights = Blueprint('flights',import_name=__name__,template_folder="templates")


@flights.route("/flights")
def flights_page():
    return render_template("flights_page.html")