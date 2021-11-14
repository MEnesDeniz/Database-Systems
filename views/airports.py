from flask import Blueprint, request, render_template


airports = Blueprint('airports',import_name=__name__,template_folder="templates")

@airports.route("/airports")
def airports_page():
    return render_template("airports_page.html")