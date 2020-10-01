import os
import requests
import urllib.parse


from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
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

def quote():

    # Contact API
    try:
        response = requests.get("https://type.fit/api/quotes")
        response.raise_for_status()

    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()

        quoteList = []

        for item in quote:

            quoteList.append({
                "text" : item["text"],
                "author" : item["author"]
            })

        return quoteList
    except (KeyError, TypeError, ValueError):
        return None


