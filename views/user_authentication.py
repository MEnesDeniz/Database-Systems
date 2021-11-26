from flask import Blueprint, request, render_template, redirect, url_for
import psycopg2 as db
import os

user_authentication = Blueprint('user_authentication', import_name=__name__,
                                template_folder="templates")



@user_authentication.route("/", methods=["GET", "POST"])
def starting_page():
    return render_template("starting_page.html")

@user_authentication.route("/login",  methods=["GET", "POST"])
def login():
    mail = request.form['Mail']
    password = request.form['password']

    connection = db.connect(os.getenv("DATABASE_URL"))
    cur = connection.cursor()

    credential_query = "SELECT mail, password FROM users WHERE mail = {mail} and password = {password}".format(mail = mail, password = password)
    cur.execute(credential_query)
    existing_account = cur.fetchone()
    if existing_account == 1:
        return redirect(url_for('app.home_page'))


