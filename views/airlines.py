from flask import Blueprint, request, render_template


airlines = Blueprint('airlines',import_name=__name__,template_folder="templates")

@airlines.route("/airlines")
def airlines_page():
    return render_template("airlines_page.html")