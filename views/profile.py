from flask import Blueprint, request, render_template, redirect, url_for
import psycopg2 as db
import os

profile = Blueprint('profile', import_name=__name__,
                     template_folder="templates")


@profile.route("/profile",  methods=["GET", "POST"])
def profile_page():
    return render_template("profile_page.html")