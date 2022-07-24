import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

# Renders a picture of apology
def apology(message, code=400):
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def log_req(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def fun(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return fun


def lookup(symbol):
    """Look up quote for city"""

    # Connect API
    try:
        headers_dict = {"Accept": "application/json", "app_id": "adf587a8", "app_key": "e4fe059f048765a5a7527fa3f68910ff", "ResourceVersion": "v4"}
        url = f"https://api.schiphol.nl/public-flights/destinations/{urllib.parse.quote_plus(symbol)}"
        


        response = requests.get(url, headers=headers_dict)
        response.raise_for_status()
    except requests.RequestException:
        return None

    
    try:
        get = response.json()
        return {
            "city": get["city"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def search(flight):

    # Connect API
    try:
        headers_dict = {"Accept": "application/json", "app_id": "adf587a8", "app_key": "e4fe059f048765a5a7527fa3f68910ff", "ResourceVersion": "v4"}
        url = f"https://api.schiphol.nl/public-flights/flights?scheduleDate={urllib.parse.quote_plus(flight)}&includedelays=false"


        response = requests.get(url, headers=headers_dict)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Specifying the return of the search
    try:
        get = response.json()
        return {
            "flights": get["flights"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def USD(value):
    return f"${value:,.2f}"
