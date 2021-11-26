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
    if request.method == 'GET':
        return render_template("login_page.html")

    elif request.method == 'POST':
        mail = request.form['Mail']
        password = request.form['password']

        connection = db.connect(os.getenv("DATABASE_URL"))
        cur = connection.cursor()

        credential_query = "SELECT mail, password FROM users WHERE mail = {mail} and password = {password}".format(
            mail=mail, password=password)
        cur.execute(credential_query)
        existing_account = cur.fetchone()
        if existing_account == 1:
            return redirect(url_for('app.home_page'))


@user_authentication.route("/register",  methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("sign_up_page.html")

    elif request.method == 'POST':
        nick_name = request.form['nick']
        mail = request.form['Mail']
        password = request.form['password']
        name = request.form['name']
        phone_number = request['phone']
        job_title = request['job']
        affiliated_company = request['affiliation']
        user_type = 0
        connection = db.connect(os.getenv("DATABASE_URL"))
        cur = connection.cursor()

        cur.execute("INSERT INTO airports(nick_name,mail,name,password,phone_number,job_title,affiliation,user_type) VALUES (%s,%s,%s,%s,%s,%s,%s)", (
            nick_name, mail, name, password, phone_number, job_title, affiliated_company, user_type))
        connection.commit()
        cur.close()
        return redirect(url_for('user_authentication.login'))
