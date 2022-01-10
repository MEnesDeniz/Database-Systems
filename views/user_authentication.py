from flask import Blueprint, request, render_template, redirect, url_for, session, flash
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
        pw = sha256(password.encode()).hexdigest()
        connection = db.connect(os.getenv("DATABASE_URL"))
        cur = connection.cursor()

        cur.execute("SELECT * FROM users WHERE mail = %s and password = %s", (mail, pw))
        existing_account = cur.fetchone()
        cur.close()
        if existing_account:
            session['loggedin'] = True
            session['id'] = existing_account[0]
            session['username'] = existing_account[1]
            session['isAdmin'] = existing_account[9]
            return redirect(url_for('home_page'))
        else:
            flash("Invalid Login Attempt!", "danger")
            return redirect(url_for('user_authentication.login'))


@user_authentication.route("/register",  methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("sign_up_page.html")
    if request.method == 'POST':
        user_name = request.form['user_name']
        mail = request.form['mail']
        password = request.form['password']
        name = request.form['name']
        surname = request.form['surname']
        phone_number = request.form['phone_number']
        gender = request.form['gender']
        habits = request.form['habit']
        if len(password.strip()) < 5:
            flash("Password must be at least 5 character!", "danger")
            return redirect(url_for("user_authentication.register"))

        if len(mail) > 30 or len(mail.strip()) == 0:
            flash("Mail must be between 1-30 characters!", "danger")
            return redirect(url_for("user_authentication.register"))

        if len(user_name) > 20 or len(user_name.strip()) == 0:
            flash("Username must be between 1-20 characters!", "danger")
            return redirect(url_for("user_authentication.register"))

        connection = db.connect(os.getenv("DATABASE_URL"))
        cur = connection.cursor()
        cur.execute("SELECT * FROM users WHERE user_name = %s", (user_name,))
        account = cur.fetchall()
        if account:
            cur.close()
            flash("This username is already taken!", "danger")
            return redirect(url_for("user_authentication.register"))

        pw_hashed = sha256(password.encode()).hexdigest()
        connection = db.connect(os.getenv("DATABASE_URL"))
        cur = connection.cursor()

        cur.execute("INSERT INTO users(user_name,mail,password, name, surname, phone , GENDER, user_description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (
            user_name, mail, pw_hashed, name, surname, phone_number, gender,habits ))
        connection.commit()
        cur.close()
        return redirect(url_for('user_authentication.login'))

@user_authentication.route("/logout")
def logout():
    session['loggedin'] = False
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('home_page'))
