from flask import Blueprint, request,   render_template, redirect, url_for, session
from hashlib import sha256
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
        return render_template("starting_page.html")
    if request.method == 'POST':
        mail = request.form['mail']
        password = request.form['pw']

        connection = db.connect(os.getenv("DATABASE_URL"))
        cur = connection.cursor()

        cur.execute("SELECT * FROM users WHERE mail = %s and password = %s", (mail, password))
        existing_account = cur.fetchone()
        cur.close()
        if existing_account:
            session['loggedin'] = True
            session['id'] = existing_account[0]
            session['username'] = existing_account[1]
            return redirect(url_for('home_page'))


@user_authentication.route("/register",  methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("sign_up_page.html")
    if request.method == 'POST':
        nick_name = request.form['nick_name']
        mail = request.form['mail']
        name = request.form['name']
        password = request.form['password']
        phone_number = request.form['phone_number']
        job_title = request.form['job_title']
        affiliated_company = request.form['affiliation']
        user_type = 0
        connection = db.connect(os.getenv("DATABASE_URL"))
        cur = connection.cursor()

        cur.execute("INSERT INTO users(nick_name,mail,name,password,phone_number,job_title,affiliation,user_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (
            nick_name, mail, name, password, phone_number, job_title, affiliated_company, user_type))
        connection.commit()
        cur.close()
        return redirect(url_for('user_authentication.login'))
