from cs50 import SQL
from flask import Flask, render_template, request, session, Response, jsonify
from flask_session import Session
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# db = SQL("sqlite:///records.db")
db = SQL("sqlite:///" + os.path.join(basedir, "records.db"))

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# don't store cache
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    session.clear()
    return render_template("index.html", normal=True, advanced=False)

@app.route("/advanced", methods=["GET"])
def advanced():
    session.clear()
    return render_template("index.html", normal=False, advanced=True)

@app.route("/recordNormal", methods=["GET", "POST"])
def record():
    # js fetch
    # get
    if request.method == "GET":
        records = db.execute("SELECT * FROM records WHERE version = 'normal' ORDER BY id DESC LIMIT 10")
        print(records)
        return jsonify(records)

    # post
    status = request.form.get("status")
    time = request.form.get("time")
    name = request.form.get("name")

    if session.get("has_submit"):
        return Response(status=204)

    if not(name.strip() == ''):
        db.execute("INSERT INTO records (status, name, time, version) VALUES (?, ?, ?, ?)",
                    status, name, time, 'normal')
        session["has_submit"] = True
    return Response(status=204)

@app.route("/recordAdvanced", methods=["GET", "POST"])
def recordAdvanced():
    # js fetch
    # get
    if request.method == "GET":
        records = db.execute("SELECT * FROM records WHERE version = 'advanced' ORDER BY id DESC LIMIT 10")
        print(records)
        return jsonify(records)

    # post
    status = request.form.get("status")
    time = request.form.get("time")
    name = request.form.get("name")

    if session.get("has_submit"):
        return Response(status=204)

    if not(name.strip() == ''):
        db.execute("INSERT INTO records (status, name, time, version) VALUES (?, ?, ?, ?)",
                    status, name, time, 'advanced')
        session["has_submit"] = True
    return Response(status=204)
