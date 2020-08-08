import os

import re
from cs50 import SQL
import random
import string
from urllib import parse
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, admin_required, getAdminIDs

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///main.db")

BASE = "http://9fb0048c-d8bb-4e3d-b3da-faa72b2b3105-ide.cs50.xyz"

# Add admin IDs to global Jinja functions
app.jinja_env.globals.update(getAdminIDs=getAdminIDs)

# Maybe add personalized link?
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        url = request.form.get("url")
        code = request.form.get("code")

        url = parse.urlsplit(url)._replace(scheme="http").geturl().replace("///", "//") # Ensure url is http
        print(url)

        if not bool(re.match("(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", url)):
            return apology("Invalid link")

        urls = [url["url"] for url in db.execute("SELECT url FROM links WHERE user=:uid", uid=session["user_id"])]

        if url in urls:
            return apology("URL already exists")

        if BASE in url:
            return apology("Cannot create already shortened link")

        if len(code) > 10:
            return apology("Custom code cannot be longer than 10 characters")

        if not bool(re.match("^[A-Za-z0-9_]*$", code)):
            return apology("Custom code may only contain letters, numbers, and underscores")

        # RANDOM LINK SNIPPET
        # letters = string.ascii_letters

        codes = [code["name"] for code in db.execute("SELECT name FROM links")]

        # code = ''.join(random.choice(letters) for i in range(6)) # 6 digits of random characters
        # while code in codes:
        #     code = ''.join(random.choice(letters) for i in range(6)) # 6 digits of random characters

        if code in codes:
            return apology("Custom code already exists")

        db.execute("INSERT INTO links (user, name, url) VALUES (:uid, :code, :url)", uid=session["user_id"], code=code, url=url)

        return render_template("added.html", link=f"{ BASE }/{code}")

    else:
        return render_template("add.html")

@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    if request.method == "POST":
        # Ensure password field is filled
        if not request.form.get("password"):
            return apology("missing password")

        # Ensure confirmation matches
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Ensure password is not the same as the old password
        old_hash = db.execute("SELECT hash FROM users WHERE id=:uid", uid=session["user_id"])[0]["hash"]
        new_hash = generate_password_hash(request.form.get("password"))

        if check_password_hash(old_hash, request.form.get("password")):
            return apology("new password cannot be the same as old password")

        # Update hash
        db.execute("UPDATE users SET hash=:new_hash WHERE id=:uid", uid=session["user_id"], new_hash=new_hash)

        # Flash and redirect
        flash("Password reset!")
        return redirect("/")
    else:
        return render_template("changepassword.html")

@app.route("/")
@login_required
def index():
    """Show all of links and metrics in table"""
    links = db.execute("SELECT id, name, clicks, timestamp, url FROM links WHERE user=:uid ORDER BY clicks DESC", uid=session["user_id"])

    return render_template("index.html", base=BASE, links=links)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
@admin_required
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username to see if it already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username does not exist
        if len(rows) > 0:
            return apology("username already exists", 403)

        # Ensure passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        uid = db.execute("INSERT INTO users (username, hash) VALUES (:username, :phash)", username=request.form.get("username"), phash=generate_password_hash(request.form.get("password")))

        # Redirect user to home page
        flash("User successfully registered!")
        return redirect("/users")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/removelink", methods=["POST"])
@login_required
def removelink():
    """ Delete link """
    link = request.form.get("link")
    short = db.execute("SELECT id FROM links WHERE id=:link AND user=:user", link=link, user=session["user_id"])

    if not short:
        return apology("No link with existing ID")

    short = short[0]["id"]

    db.execute("DELETE FROM links WHERE id=:linkid", linkid=short)
    return redirect("/")

@app.route("/removeuser", methods=["POST"])
@admin_required
def removeuser():
    """ Delete non-admin user """
    user = request.form.get("user")
    uid = db.execute("SELECT id FROM users WHERE username=:user", user=user)

    if not uid:
        return apology("User does not exist")

    uid = uid[0]["id"]

    if uid in getAdminIDs():
        return apology("User is not an administrator")

    db.execute("DELETE FROM users WHERE id=:uid", uid=uid)
    db.execute("DELETE FROM links WHERE user=:uid", uid=uid)
    return redirect("/users")

@app.route("/users")
@admin_required
def users():
    """View a list of users"""
    users = db.execute("SELECT id, username from USERS")
    return render_template("users.html", users=users, adminIDs=getAdminIDs())

@app.route("/<string:short>")
def short(short):
    shorts = db.execute("SELECT name, url FROM links")

    for url in shorts:
        if short == url["name"]:
            db.execute("UPDATE links SET clicks=clicks+1 WHERE name=:short", short=short)
            return redirect(url["url"])

    return apology("Page not found", 404)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)