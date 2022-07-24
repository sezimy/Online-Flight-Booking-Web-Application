import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_mail import Mail, Message 
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime



from helpers import apology, log_req, lookup, USD, search

# Configuring the application
app = Flask(__name__)


# Configuring the Flask_Mail
app.config["MAIL_DEFAULT_SENDER"] = "amsterdamairlineams@gmail.com"
app.config["MAIL_PASSWORD"] = "13579azsxdcfv!"
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "amsterdamairlineams@gmail.com"

mail = Mail(app)



# Templates should auto-reload
app.config["TEMPLATES_AUTO_RELOAD"] = True


app.jinja_env.filters["usd"] = USD

# Configures session, so that it uses filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connects SQL database to the webapplication
db = SQL("sqlite:///airport.db")

# Checks if API key was provided
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Main page
@app.route("/")
@log_req
def index():
    # Query that gets the flight details of the current user from the database 
    rows = db.execute("SELECT destination, date, time, flight_number, class, num_passengers FROM tickets WHERE user_id = ?",  session["user_id"])
    # Query that gets the amount of cash that the current user has
    money = db.execute("SELECT cash FROM users WHERE id = ?",  session["user_id"])
    cash=money[0]["cash"]

    return render_template("index.html", rows=rows, cash=cash)

# Page that shows all flights booked by the current user so that the user can cancel any of them
@app.route("/back", methods=["GET", "POST"])
@log_req
def back():
    # Query that gets the flight details of the current user from the database 
    rows = db.execute("SELECT id, destination, date, time, flight_number, class, num_passengers FROM tickets WHERE user_id = ?",  session["user_id"])

    # Sends the result of query to the page back.html
    return render_template("back.html", rows=rows)

# This function deletes the flight from the user's flights
@app.route("/cancel", methods=["GET", "POST"])
@log_req
def cancel():
    # If the button is clicked and cancel function is called
    if request.method == "POST":
        # Gets the flight id from the input with name "id"
        id = request.form.get("id")
        rows = db.execute("SELECT num_passengers FROM tickets WHERE id = ?",  id)
        passengers = rows[0]["num_passengers"]
        row = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash=int(row[0]["cash"])

        # Only 75% percent of the total cost will be returned
        total=passengers*0.75*2000
        back=cash+total
        db.execute("DELETE FROM tickets WHERE id = ?", id)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", back, session["user_id"])
        return redirect("/")
    else:
        return render_template("back.html")

# This function changes the password
@app.route("/changepswd", methods=["GET", "POST"])
@log_req
def changepswd():
    if request.method == "POST":

        # Gets the new password entered by user from the input called "password"
        password = request.form.get("password")

        if not password:
            return apology("Must provide new password", 403)

        # Updates the database by replacing the old password with new one for the current user
        db.execute("UPDATE users SET password = ? WHERE id = ?", generate_password_hash(password), session["user_id"])
        return redirect("/")
    else:
        return render_template("password.html")

# This function adds cash to personal balance of the current user
@app.route("/addcash", methods=["GET", "POST"])
@log_req
def addcash():
    if request.method == "POST":
        
        money = request.form.get("cash")

        # Checks if the user entered valid data
        if not money or not money.isdigit() or int(money)<0:
            return apology("Must provide the amount of cash, and please enter only positive numeric characters", 403)

        rows = db.execute("SELECT cash FROM users WHERE id = ?",  session["user_id"])
        cash=int(rows[0]["cash"])
        total=cash+int(money)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", total, session["user_id"])
        return redirect("/")
    else:
        return render_template("cash.html")


@app.route("/book", methods=["GET", "POST"])
@log_req
def book():
    if request.method == "POST":

        # Gets the flight details from the named inputs respectively
        destination = request.form.get("destination")
        date = request.form.get("date")
        time = request.form.get("time")
        flight_number = request.form.get("flight_number")
        return render_template("book.html", destination=destination, date=date, time=time, flight_number=flight_number)
    else:
        return render_template("search.html")

# This function inserts into the database details of the flight booked by the current user
@app.route("/submit", methods=["GET", "POST"])
@log_req
def submit():
    if request.method == "POST":
        # The destination
        destination = request.form.get("destination")
        # The date of flight
        date = request.form.get("date")
        # The time of flight
        time = request.form.get("time")
        # The flight number
        flight_number = request.form.get("flight_number")
        #The email of user
        email = request.form.get("email")
        # The number if passengers
        num_passengers = int(request.form.get("passengers"))
        # The class of the flight
        p_class = request.form.get("class")
        # Cost of the flight
        cost = num_passengers*2000
        # The current cash of the user
        rows = db.execute("SELECT cash FROM users WHERE id = ?",  session["user_id"])
        cash=int(rows[0]["cash"])
        # The remaining cash of user after the purchase of a ticket
        total=cash-cost

        # Checks if user has enough money for purchase of ticket
        if total<0:
            return apology("Sorry, you need more cash")
        # Inserts all flight details into the database
        db.execute("INSERT INTO tickets (user_id, destination, date, time, flight_number, class, num_passengers) VALUES(?, ?, ?, ?, ?, ?, ?)", session["user_id"], destination, date, time, flight_number, p_class, num_passengers)
        # Updates the cash of the current user
        db.execute("UPDATE users SET cash = ? WHERE id = ?", total, session["user_id"])
        # Sends email to the mailbox of the current user
        message = Message("You succesfully booked your ticket!", recipients=[email])
        mail.send(message)
        return redirect("/")
    else:
        return render_template("search.html")







@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget the current user
    session.clear()


    if request.method == "POST":

        # Checks if the username was provided
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Checks if the password was provided
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Searches for the username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Checks if there is a match 
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remembers the current user
        session["user_id"] = rows[0]["id"]


        return redirect("/")


    else:
        return render_template("login.html")




@app.route("/logout")
def logout():
    """Log user out"""

    # Forget the current user
    session.clear()

    return redirect("/")


@app.route("/find", methods=["GET", "POST"])
@log_req
def find():
    

    if request.method == "POST":

        # The code of the city
        c = request.form.get("city")
        # Returns the code of the city in uppercase letters
        des = c.upper()
        # The date of flight
        flight_date = request.form.get("date")
        # Searches for the destinations based on the code entered by user
        city = lookup(des)
        # Checks if there is such city code in teh database
        if city == None:
            return apology("invalid city", 400)
        # Searches for the flights on date entered by the user
        date = search(flight_date)

        # Name of the city
        name=city["city"]
        # Accessing the list inside of the dictionary
        d=date["flights"]
        # Creates two empty lists
        times = []
        number = []
 
        # Iterates through each flight in the database
        for i in range(len(d)):
            # Accesses the destinations dictionary inside the list
            k=d[i]["route"]
            # Accesses the dates dictionary inside the list
            b=d[i]["scheduleTime"]
            # Accesses the flightName dictionary inside the list
            v=d[i]["flightName"]
            # Accesses the code of citites inside the dictionary
            r=k["destinations"]
            # For each city inside the dictionary
            for y in range(len(r)):
                t=r[y]
                # Checks if the code entered by the user mathces with codes of cities inside the dictionary
                if des==t:
                    # If there is a mtch, the flight's time and number is added to the list
                    times.append(b) 
                    number.append(v)
        # Checks if there are available fligths for the destination and date entered by user
        if not times:
            return apology("No available flights", 400)
            
        return render_template("searched.html", name=name, times=times, numbertime=zip(times, number), flight_date=flight_date, b=b, v=v, r=r)
    else: 
        return render_template("search.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Checks if the username was provided
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Checks if the password was provided
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password and consfirm it", 400)
        
        elif request.form.get("password")!=request.form.get("confirmation"):
            return apology("your password must match with confiration", 400)
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 0:
            return apology("such username already exists", 400)

        db.execute("INSERT INTO users (username, password) VALUES(?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))
        return render_template("login.html")
    
    else:
        return render_template("register.html")




def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)



for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
