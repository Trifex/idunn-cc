import os
import requests
import urllib.parse

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps

db = SQL("sqlite:///main.db")

def getAdminIDs():
    ids = db.execute("SELECT id FROM users WHERE admin=1")
    ids = [idnum["id"] for idnum in ids]

    return ids

def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("error.html", top=code, bottom=message.upper()), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") not in getAdminIDs():
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function