import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import random

from helpers import apology, login_required, quote

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
db = SQL("sqlite:///fp.db")


@app.route("/")
@login_required
def index():
    """Show quote of the day"""

    quoteList = quote()

    #Generates a random number for the index of the list of quotes
    index = random.randint(1,50)

    #Makes sure that anonymous is displayed if there is no author
    if quoteList[index]["author"] == None:
       quoteList[index]["author"] = "Anonymous"

    author = quoteList[index]["author"]
    text = quoteList[index]["text"]

    return render_template("index.html", text=text, author=author)



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


@app.route("/write", methods=["GET", "POST"])
@login_required
def write():
    """Get writing page."""

    if request.method == "GET":
        return render_template("write.html")

    #Gets form input and inserts it to the database
    else:
        textarea = request.form.get("textarea")
        color = request.form.get("color")

        if color == None:
            return apology("Please pick a color")

        db.execute("INSERT INTO diary (id, textarea, color) VALUES (:id, :textarea, :color)", id=session['user_id'], textarea=textarea, color=color)
        return redirect("/entries")

@app.route("/register", methods=["GET", "POST"])
def register():

    """Register user"""

    if request.method == "POST":

         # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        #Gets register input
        username = request.form.get("username")
        hashpw = generate_password_hash(request.form.get("password"))

        #Inserts the new user credentials to the database
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hashpw)
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/entries", methods=["GET", "POST"])
def entries():
    """ See entries """

    if request.method == "GET":

        #Gets all data from the specific user
        data = db.execute("SELECT * FROM diary WHERE id=:id ORDER BY date DESC", id=session['user_id'])

        datums = []

        #Appends the data into a list
        for row in data:
            datums.append({
                "color" : row["color"],
                "textarea" : row["textarea"][:50],
                "date" : row["date"],
                "journalid" : row["journalid"]
                })

        return render_template("entries.html", datums=datums)


@app.route("/view/<journalid>", methods=["GET", "POST"])
def view(journalid):
    """ See contents of clicked entry """

    #Gets the data of the specific journal id
    data = db.execute("SELECT textarea, date, journalid, color FROM diary WHERE journalid=:journalid", journalid=journalid)

    textarea = data[0]["textarea"]
    date = data[0]["date"]
    journalid = data[0]["journalid"]
    color = data[0]["color"]

    return render_template("view.html", textarea=textarea, date=date, journalid=journalid, color=color)


@app.route("/edit/<journalid>", methods=["GET", "POST"])
@login_required
def edit(journalid):
    """Get editing page."""

    if request.method == "GET":

        #Gets the data of the specific journal id
        data = db.execute("SELECT textarea, date, journalid FROM diary WHERE journalid=:journalid", journalid=journalid)

        textarea = data[0]["textarea"]
        date = data[0]["date"]
        journalid = data[0]["journalid"]

        return render_template("edit.html", textarea=textarea, date=date, journalid=journalid)


    else:
        #Gets the new data from the form if method is post
        newtextarea = request.form.get("textarea")
        newcolor = request.form.get("color")

        db.execute("UPDATE diary SET textarea=:textarea, color=:color WHERE journalid=:journalid", textarea=newtextarea, color=newcolor, journalid=journalid)

        return redirect("/entries")


@app.route("/track")
@login_required
def track():

    #Gets all data from the user
    data = db.execute("SELECT color, date FROM diary WHERE id=:id ORDER BY date DESC", id=session['user_id'])

    colors = []

    #Appends data to a list
    for row in data:
        colors.append({
            "color": row["color"],
            "date": row["date"][0:10]
        })


    return render_template("track.html", colors=colors)

@app.route("/delete/<journalid>", methods=["GET", "POST"])
def delete(journalid):

    #Deletes data of the specific journal id
    db.execute("DELETE FROM diary WHERE journalid=:journalid", journalid=journalid)

    return redirect("/entries")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
