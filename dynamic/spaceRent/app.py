from cs50 import SQL
from flask import Flask, render_template, request, session, redirect, url_for #, Response, jsonify, flash
from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
# from flask_paginate import Pagination
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import re
import math
from helper import check_valid_datetime
import calendar

app = Flask(__name__)

articlesDb = SQL("sqlite:///articles.db")
ordersDb = SQL("sqlite:///orders.db")
spacesDb = SQL("sqlite:///spaces.db")
usersDb = SQL("sqlite:///users.db")

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

# client side #
@app.route("/", methods=["GET"])
def index():
    news = articlesDb.execute("SELECT * FROM news ORDER BY date DESC LIMIT 3")
    events = articlesDb.execute("SELECT * FROM events ORDER BY date DESC LIMIT 2")

    # the select options for searching rooms
    locations = spacesDb.execute("SELECT location FROM spaces ORDER BY id ASC")
    places = []
    for location in locations:
        if (location["location"] not in places):
            places.append(location["location"])

    return render_template("/client/index.html", login=session.get('login'), current_username=session.get('current_username'), news=news, events=events, places=places)


@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method == "GET"):
        if (session.get('login')):
            return redirect('/')
        return render_template("/client/login.html", login=session.get("login"))

    # POST    
    # check db is not empty table
    user_count = usersDb.execute("SELECT * FROM users")
    if (len(user_count) == 0):
        login_fail = True
        return render_template("/client/login.html", login_fail=login_fail, login=session.get("login"))

    login_username = request.form.get("username")
    login_password = request.form.get("password")

    # not existing username
    db_username = usersDb.execute("SELECT username FROM users WHERE username = ?", login_username)[0]["username"]
    if not (db_username) or not (login_username == db_username):
        login_fail = True
        return render_template("/client/login.html", login_fail=login_fail, login=session.get("login"))

    # wrong password
    db_password = usersDb.execute("SELECT password FROM users WHERE username = ?", login_username)[0]["password"]
    if not (db_password) or not (check_password_hash(db_password, login_password)):
        login_fail = True
        return render_template("/client/login.html", login_fail=login_fail, login=session.get("login"))

    # login success
    session["login"] = True
    session["current_username"] = login_username
    return redirect("/")

@app.route("/logout", methods=["GET"])
def logout():
    del session["login"]
    del session["current_username"]
    return redirect("/")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if (request.method == "GET"):
        if (session.get('login')):
            return redirect('/')
        return render_template("/client/signup.html", login=session.get("login"))
    
    # POST
    # get today date
    today = datetime.date.today()

    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    birthday = request.form.get("birthday")
    lag = request.form.get("lag") # milliseconds
    agree = request.form.get("agree")

    # lag time absolute value should never over than 24 hours
    if (abs(int(lag)) > 24 * 60 * 60 * 1000) or (lag.strip() == ""):
        signup_fail = True
        return render_template("/client/signup.html", signup_fail=signup_fail, login=session.get("login"))

    # if the users is 18 year-old or not, should compare to his local time zone
    today = today + datetime.timedelta(milliseconds=int(lag))

    # no empty
    if (username.strip() == "") or (password.strip() == "") or (confirmation.strip() == "") or (name.strip() == "") or (email.strip() == "") or (phone.strip() == "") or (birthday.strip() == "") or (agree == None):
        signup_fail = True
        return render_template("/client/signup.html", signup_fail=signup_fail, login=session.get("login"))

    # not space
    if (" " in username) or (" " in password) or (" " in confirmation) or (" " in name) or (" " in email) or (" " in phone) or (" " in birthday):
        signup_fail = True
        return render_template("/client/signup.html", signup_fail=signup_fail, login=session.get("login"))
    
    # wrong confirmation
    if not (password == confirmation):
        signup_fail = True
        return render_template("/client/signup.html", signup_fail=signup_fail, login=session.get("login"))
    
    # check format
    # email format
    if not ('@' in email):
        signup_fail = True
        return render_template("/client/signup.html", signup_fail=signup_fail, login=session.get("login"))

    # invalid birthday date
    birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d').date()
    if (birthday > today):
        signup_fail = True
        return render_template("/client/signup.html", signup_fail=signup_fail, login=session.get("login"))
    
    # age must need be over 18
    # age formula source code url:
    # https://stackoverflow.com/questions/2217488/age-from-birthdate-in-python
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    if (age < 18):
        signup_fail = True
        return render_template("/client/signup.html", signup_fail=signup_fail, login=session.get("login"))
    
    # username or password length is not long enough
    if (len(username) < 6) or (len(password) < 8):
        signup_fail = True
        return render_template("/client/signup.html", signup_fail=signup_fail, login=session.get("login"))

    # username or password doesn't fit require format (uppercase or lowercase or number)
    if not (re.search(r'\d', username) and re.search(r'[a-zA-Z]', username)) or not (re.search(r'\d', password) and re.search(r'[a-z]', password) and re.search(r'[A-Z]', password)):
        signup_fail = True
        return render_template("/client/signup.html", signup_fail=signup_fail, login=session.get("login"))
    
    # no repeat username is available to apply
    usernames = usersDb.execute("SELECT username FROM users WHERE username = ?", username)

    # the username is occupied
    if not (len(usernames) == 0):
        repeat_username = True
        return render_template("/client/signup.html", repeat_username=repeat_username, login=session.get("login"))
    
    # valid apply, apply success
    password = generate_password_hash(password)
    usersDb.execute("INSERT INTO users (username, password, name, email, phone, birthday) VALUES (?, ?, ?, ?, ?, ?)",
                    username, password, name, email, phone, birthday)
    signup_success = True
    return render_template("/client/signup.html", signup_success=signup_success, login=session.get("login"))


@app.route("/news", methods=["GET"])
def news():
    # read specific news (recognized by id)
    if (request.args.get("id")):
        id = request.args.get("id")
        article = articlesDb.execute("SELECT * FROM news WHERE id = ?", id)[0]
        return render_template("/client/detail_info_article.html", article=article, login=session.get("login"))

    # all news from database if user does't search any keyword, and order by date (from latest to earliest)
    all = articlesDb.execute("SELECT * FROM news ORDER BY date DESC")

    # all news from database if user searches any keyword, and order by date (from latest to earliest)
    search = request.args.get("search")
    if (search):
        all = articlesDb.execute("SELECT * FROM news WHERE title LIKE ? ORDER BY date DESC", '%'+search+'%')

    # make pages and assign news to each page
    per_page = 5
    total_pages = 0
    if (len(all) % per_page):
        total_pages = int((len(all) / per_page) + 1)
    else:
        total_pages = int((len(all) / per_page))
    # default page is page 1
    page = int(request.args.get('page', 1))
    if (page > total_pages):
        page = total_pages
    # assign news to each page
    start = (page - 1) * per_page
    end = start + per_page
    show_news_index = all[start:end]
    return render_template("/client/news.html", news=show_news_index, total_pages=total_pages, page=page, search=search, login=session.get('login'), current_username=session.get('current_username'))


@app.route("/events", methods=["GET"])
def events():
    # read specific events (recognized by id)
    if (request.args.get("id")):
        id = request.args.get("id")
        article = articlesDb.execute("SELECT * FROM events WHERE id = ?", id)[0]
        return render_template("/client/detail_info_article.html", article=article, login=session.get("login"))
    
    # all events from database if user does't search any keyword, and order by date (from latest to earliest)
    all = articlesDb.execute("SELECT * FROM events ORDER BY date DESC")
    
    # all events from database if user searches any keyword, and order by date (from latest to earliest)
    search = request.args.get("search")
    if (search):
        all = articlesDb.execute("SELECT * FROM events WHERE title LIKE ? ORDER BY date DESC", '%'+search+'%')

    # make pages and assign news to each page
    per_page = 5
    total_pages = 0
    if (len(all) % per_page):
        total_pages = int((len(all) / per_page) + 1)
    else:
        total_pages = int((len(all) / per_page))
    # default page is page 1
    page = int(request.args.get('page', 1))
    if (page > total_pages):
        page = total_pages
    # assign news to each page
    start = (page - 1) * per_page
    end = start + per_page
    show_events_index = all[start:end]
    return render_template("/client/events.html", events=show_events_index, total_pages=total_pages, page=page, search=search, login=session.get('login'), current_username=session.get('current_username'))

@app.route("/search", methods=["GET"])
def search():
    # create select options for html
    locations = spacesDb.execute("SELECT location FROM spaces ORDER BY id ASC")
    places = []
    for location in locations:
        if (location["location"] not in places):
            places.append(location["location"])

    # when user choose a room from all available results 
    if (request.args.get("room")):
        # args all come from templates (result.html) url_for
        room = request.args.get("room")
        local_start = request.args.get("start")
        local_end = request.args.get("end")
        space = spacesDb.execute("SELECT * FROM spaces WHERE name = ?", room)[0]
        comments = ordersDb.execute("SELECT comment FROM comments WHERE space = ? AND NOT comment = '' AND status = ? ORDER BY id DESC LIMIT 5", room, 'show')
        equipment = spacesDb.execute("SELECT equipments FROM spaces WHERE name = ?", room)[0]["equipments"]
        equipments = equipment.split(", ")

        # check if provide any equipment
        nothing = True
        for equipment in equipments:
            if not (equipment == 'None'):
                nothing = False

        return render_template("/client/detail_info_search.html", space=space, start=local_start, end=local_end, comments=comments, equipments=equipments, nothing=nothing, login=session.get("login"), places=places)
    
    # args all come from templates (index.html) search form
    place = request.args.get("place")
    local_start = request.args.get("start")
    local_end = request.args.get("end")
    lag = request.args.get("lag")
    headcount = request.args.get("headcount")

    # convert time format. local meas user's location. and local time will be useful later.
    local_start = datetime.datetime.fromisoformat(local_start)
    local_end = datetime.datetime.fromisoformat(local_end)
    now = datetime.datetime.now()

    # convert local time to server local time to compare data in database to check if available space
    start = local_start + datetime.timedelta(milliseconds=int(lag))
    end = local_end + datetime.timedelta(milliseconds=int(lag))

    available_spaces_names = [] # a list with pure space name
    available_spaces_detail = [] # a list with all rooms information

    # lag time absolute value should never over than 24 hours
    if (abs(int(lag)) > 24 * 60 * 60 * 1000) or (lag.strip() == ""):
        wrong_date = True
        return render_template("/client/result.html", place=place, start=local_start, end=local_end, headcount=headcount, available_spaces_detail=available_spaces_detail, wrong_date=wrong_date, login=session.get("login"), places=places)

    valid_time = check_valid_datetime(now,start,end)
    if not (valid_time):
        wrong_date = True
        return render_template("/client/result.html", place=place, start=local_start, end=local_end, headcount=headcount, available_spaces_detail=available_spaces_detail, wrong_date=wrong_date, login=session.get("login"), places=places)
    
    # check if user select a place that not exists in database
    if (place not in places):
        return render_template("/client/result.html", place=place, start=local_start, end=local_end, headcount=headcount, available_spaces_detail=available_spaces_detail, login=session.get("login"), places=places)

    # the spaces which are the place user choosing and is bigger than (or just fit) his need(headcount)
    spaces = spacesDb.execute("SELECT name FROM spaces WHERE location LIKE ? AND capacity >= ?", '%'+place+'%', headcount)
    # get pure spaces names that bigger than (or just fit) his need(headcount)
    spaces_names = [] # a list with pure space name
    for space in spaces:
        spaces_names.append(space["name"])

    # get those spaces names that have any valid (not be canceled) order
    spaces_names_have_orders = [] # a list with pure space name
    for space_name in spaces_names: # a list with pure space name
        space_orders = ordersDb.execute("SELECT * FROM orders WHERE space = ? AND NOT status = ? ORDER BY start ASC", space_name, 'Canceled')
        if (len(space_orders) == 0):
            available_spaces_names.append(space_name)
            available_spaces_names.sort()
        else:
            spaces_names_have_orders.append(space_name)
            spaces_names_have_orders.sort()

    # to find if any available time gap to make a new order
    for space_name_has_orders in spaces_names_have_orders: # a list with pure space name
        orders = ordersDb.execute("SELECT * FROM orders WHERE space = ? AND NOT status = ? ORDER BY start ASC", space_name_has_orders, 'Canceled')

        is_later = False
        check_count = 0

        for order in orders:
            check_count = check_count + 1
            # new order compare with the first earliest existed order
            if (check_count == 1):
                # earlier than the first earliest existed order
                if (start < datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S")) and (end <= datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S")):
                    available_spaces_names.append(space_name_has_orders)
                    available_spaces_names.sort()
                    break
                # later than the first earliest existed order
                elif (start >= datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")) and (end > datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")):
                    # only one order existed
                    if (len(orders) == 1):
                        available_spaces_names.append(space_name_has_orders)
                        available_spaces_names.sort()
                        break
                    else:
                        is_later = True
                        continue
                # overlap
                else:
                    is_later = False
                    break

            # new order compare with the latest existed order
            elif (check_count == len(orders)):
                # later than the latest existed order
                if (start >= datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")) and (end > datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")):
                    available_spaces_names.append(space_name_has_orders)
                    available_spaces_names.sort()
                    break
                # earlier than the latest existed order
                elif (is_later) and ((start < datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S")) and (end <= datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S"))):
                    available_spaces_names.append(space_name_has_orders)
                    available_spaces_names.sort()
                    break
                # overlap
                else:
                    is_later = False
                    break
            # between two orders
            else:
                # find the empty and available time
                if (is_later) and (start < datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S")) and (end <= datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S")):
                    is_later = False
                    available_spaces_names.append(space_name_has_orders)
                    available_spaces_names.sort()
                    break
                # later than the current comparing order (make timeline compare step move forward)
                elif (is_later) and (start >= datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")) and (end > datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")):
                    is_later = True
                    continue
                # overlap
                else:
                    is_later = False
                    break


    for available_space_name in available_spaces_names: # a list with pure space name
        available_spaces_detail.append(spacesDb.execute("SELECT * FROM spaces WHERE name = ?", available_space_name)[0])# a list with all rooms information

    # make pages and assign rooms to each page
    per_page = 8
    total_pages = 0
    if (len(available_spaces_detail) % per_page):
        total_pages = int((len(available_spaces_detail) / per_page) + 1)
    else:
        total_pages = int((len(available_spaces_detail) / per_page))

    page = int(request.args.get('page', 1))
    if (page > total_pages):
        page = total_pages

    result_start_index = (page - 1) * per_page
    result_end_index = result_start_index + per_page
    show_results_index = available_spaces_detail[result_start_index:result_end_index]

    return render_template("/client/result.html", results=show_results_index, page=page, total_pages=total_pages, place=place, start=local_start, end=local_end, headcount=headcount, login=session.get("login"), places=places)

@app.route("/order", methods=["GET", "POST"])
def order():
    # order GET assigns the data which user filled in the search form to order page automatically
    if request.method == "GET":
        if not (session.get("login")):
            return redirect("/login")
        room = request.args.get("room")
        start = request.args.get("start")
        end = request.args.get("end")

        info = spacesDb.execute("SELECT * FROM spaces WHERE name = ?", room)[0]

        return render_template("/client/order.html", start=start, end=end, info=info, login=session.get("login"))
    
    # POST is making a new order
    room = request.form.get("room")
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    start = request.form.get("start")
    end = request.form.get("end")
    lag = request.form.get("lag")
    total = request.form.get("total")
    # card = request.form.get("card")
    note = request.form.get("note").strip()
    agree = request.form.get("agree")

    info = spacesDb.execute("SELECT * FROM spaces WHERE name = ?", room)[0]
    orders = ordersDb.execute("SELECT * FROM orders WHERE space = ? AND NOT status = ?", room, 'Canceled')
    location = spacesDb.execute("SELECT location FROM spaces WHERE name = ?", room)[0]["location"]

    # lag time absolute value should never over than 24 hours
    if (abs(int(lag)) > 24 * 60 * 60 * 1000) or (lag.strip == ""):
        order_fail = True
        return render_template("/client/order.html", order_fail=order_fail, form=request.form, info=info, login=session.get("login"))

    # no empty
    if (room.strip() == "") or(name.strip() == "") or (email.strip() == "") or (phone.strip() == "") or (start.strip() == "") or (end.strip() == "") or (total.strip() == "") or (agree == None):
        order_fail = True
        return render_template("/client/order.html", order_fail=order_fail, form=request.form, info=info, login=session.get("login"))
    
    # check format
    if not('@' in email):
        order_fail = True
        return render_template("/client/order.html", order_fail=order_fail, form=request.form, info=info, login=session.get("login"))
    
    # get current time and convert time format
    now = datetime.datetime.now()
    start = datetime.datetime.fromisoformat(start)
    end = datetime.datetime.fromisoformat(end)

    # convert local time to server local time to compare data in database to check if available space
    start = start + datetime.timedelta(milliseconds=int(lag))
    end = end + datetime.timedelta(milliseconds=int(lag))

    # over than 1 min equals to 1 hour to calculate the fee
    duration = math.ceil((end - start).total_seconds() / 60 / 60)
    per_price = spacesDb.execute("SELECT price FROM spaces WHERE name = ?", room)[0]["price"]
    total_check = duration * per_price

    # if user hack the total value by changing input value from frontend (html or js)
    if not (int(total) == total_check):
        order_fail = True
        return render_template("/client/order.html", order_fail=order_fail, form=request.form, info=info, login=session.get("login"))

    valid_time = check_valid_datetime(now,start,end)
    if not (valid_time):
        order_fail = True
        return render_template("/client/order.html", order_fail=order_fail, form=request.form, info=info, login=session.get("login"))

    # if there's no any order, it means any valid request is acceptable order
    if (len(orders) == 0):
        ordersDb.execute("INSERT INTO orders (username, email, phone, name, start, end, duration, application_date, space, location, total, note, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", session.get("current_username"), email, phone, name, start, end, duration, now, room, location, total, note, 'Deal')
        return redirect("/history") 

    # check if any available time gap to make a new order
    is_later = False
    check_count = 0

    for order in orders:
        check_count = check_count + 1
        # new order compare with the first earliest existed order
        if (check_count == 1):
            # earlier than the first earliest existed order
            if (start < datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S")) and (end <= datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S")):
                break
            # later than the first earliest existed order
            elif (start >= datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")) and (end > datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")):
                # only one order existed
                if (len(orders) == 1):
                    break
                else:
                    is_later = True
                    continue

            # overlap
            else:
                overlap = True
                return render_template("/client/order.html", overlap=overlap, form=request.form, info=info, login=session.get("login"))


        # new order compare with the latest existed order
        elif (check_count == len(orders)):
            # later than the latest existed order
            if (start >= datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")) and (end > datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")):
                break
            # earlier than the latest existed order
            elif (is_later) and ((start < datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S")) and (end <= datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S"))):
                break
            # overlap
            else:
                overlap = True
                return render_template("/client/order.html", overlap=overlap, form=request.form, info=info, login=session.get("login"))

        # between two orders
        else:
            # find the empty and available time
            if (is_later) and (start < datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S")) and (end <= datetime.datetime.strptime(order["start"], "%Y-%m-%d %H:%M:%S")):
                is_later = False
                break
            # later than the current comparing order (make timeline compare step move forward)
            elif (is_later) and (start >= datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")) and (end > datetime.datetime.strptime(order["end"], "%Y-%m-%d %H:%M:%S")):
                is_later = True
                continue
            # overlap
            else:
                overlap = True
                return render_template("/client/order.html", overlap=overlap, form=request.form, info=info, login=session.get("login"))
        
    ordersDb.execute("INSERT INTO orders (username, email, phone, name, start, end, duration, application_date, space, location, total, note, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", session.get("current_username"), email, phone, name, start, end, duration, now, room, location, total, note, 'Deal')
    return redirect("/history")

@app.route("/history", methods=["GET"])
def history():
    if not (session.get("login")):
        return redirect('/')
    # user can only review his history orders
    current_username = session.get("current_username")
    orders = ordersDb.execute("SELECT * FROM orders WHERE username = ? ORDER BY id DESC", current_username)
    # if user want to check specific order (recognized by order's id)
    if (request.args.get("id")):
        order_id = request.args.get("id")
        current_username = session.get("current_username")
        order = ordersDb.execute("SELECT * FROM orders WHERE id = ? AND username = ?", order_id, current_username)
        # prevent user type invalid order id in URL arg
        if (len(order) == 0):
            return redirect("/history")
        
        # show the comment status about if the user leave a comment for the order or not
        space = spacesDb.execute("SELECT * FROM spaces WHERE name = ?", order[0]["space"])[0]
        commented = False
        if not (order[0]["comment"] == None):
            commented = True

        # check if user can cancel the order or not, it should be at least before over than 48 hours
        now = datetime.datetime.now()
        start = datetime.datetime.fromisoformat(order[0]["start"])
        end = datetime.datetime.fromisoformat(order[0]["end"])

        before48 = False
        if (now + datetime.timedelta(hours=48) < start):
            before48 = True
        
        finished = False
        if (now > end):
            finished = True
        return render_template("/client/detail_order.html", order=order[0], space=space, commented=commented, before48=before48, finished=finished, login=session.get("login"))

    # make pages and assign news to each page
    per_page = 5
    total_pages = 0
    if (len(orders) % per_page):
        total_pages = int((len(orders) / per_page) + 1)
    else:
        total_pages = int((len(orders) / per_page))

    page = int(request.args.get('page', 1))
    if (page > total_pages):
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    show_orders_index = orders[start:end]

    return render_template("/client/history.html", orders=show_orders_index, total_pages=total_pages, page=page, login=session.get("login"))

@app.route("/profile", methods=["GET"])
def profile():
    if not (session.get("login")):
        return redirect('/')

    current_username = session.get("current_username")
    info = usersDb.execute("SELECT * FROM users WHERE username = ?", current_username)[0]

    return render_template("/client/profile.html", login=session.get("login"), info=info)

@app.route("/update", methods=["POST"])
def update():
    email = request.form.get("email")
    phone = request.form.get("phone")
    current_username = session.get("current_username")
    info = usersDb.execute("SELECT * FROM users WHERE username = ?", current_username)[0]

    # check format
    if (email.strip() == "") or (phone.strip() == "") or not ("@" in email):
        update_fail = True
        return render_template("/client/profile.html", login=session.get("login"), info=info, update_fail=update_fail)
    
    # valid update
    usersDb.execute("UPDATE users SET email = ?, phone = ? WHERE username = ?", email, phone, current_username)
    info = usersDb.execute("SELECT * FROM users WHERE username = ?", current_username)[0]
    update_success = True
    return render_template("/client/profile.html", login=session.get("login"), info=info, update_success=update_success)

@app.route("/reset", methods=["POST"])
def reset():
    origin = request.form.get("origin")
    new = request.form.get("new")
    confirmation = request.form.get("confirmation")

    current_username = session.get("current_username")
    info = usersDb.execute("SELECT * FROM users WHERE username = ?", current_username)[0]
    
    # wrong password
    if not(check_password_hash(info["password"], origin)):
        reset_fail = True
        return render_template("/client/profile.html", login=session.get("login"), info=info, reset_fail=reset_fail)

    # check format
    if not (new == confirmation):
        reset_fail = True
        return render_template("/client/profile.html", login=session.get("login"), info=info, reset_fail=reset_fail)
    
    if (len(new) < 8):
        reset_fail = True
        return render_template("/client/profile.html", login=session.get("login"), info=info, reset_fail=reset_fail)

    if not (re.search(r'\d', new) and re.search(r'[a-z]', new) and re.search(r'[A-Z]', new)):
        reset_fail = True
        return render_template("/client/profile.html", login=session.get("login"), info=info, reset_fail=reset_fail)

    # valid reset and logout immediately
    usersDb.execute("UPDATE users SET password = ? WHERE username = ?", generate_password_hash(new), current_username)
    return redirect("/logout")

@app.route("/cancel", methods=["POST"])
def cancel():
    id = request.form.get("id")
    agree = request.form.get("agree")
    current_username = session.get("current_username")
    order = ordersDb.execute("SELECT * FROM orders WHERE id = ? AND username = ?", id, current_username)

    # wrong id, if user hack id input
    if (len(order) == 0) or (agree == None):
        return redirect("/history")
    
    # check if before over than 48 hours, if not, no executing and redirect immediately
    now = datetime.datetime.now()
    start = datetime.datetime.fromisoformat(order[0]["start"])
    if (now + datetime.timedelta(hours=48) < start):
        ordersDb.execute("UPDATE orders SET status = ? WHERE id = ? AND username = ?", 'Canceled', id, current_username)
    return redirect('/history')

@app.route("/comment", methods=["POST"])
def comment():
    id = request.form.get("id")
    comment = request.form.get("comment").strip()
    agree = request.form.get("agree").strip()
    current_username = session.get("current_username")
    order = ordersDb.execute("SELECT * FROM orders WHERE id = ? AND username = ?", id, current_username)

    # wrong id, if user hack id input
    if (len(order) == 0):
        return redirect("/history")
    
    space = spacesDb.execute("SELECT * FROM spaces WHERE name = ?", order[0]["space"])[0]

    # if empty or not checked checkbox
    if (agree == None) or (len(comment) == 0):
        not_checked = True
        return render_template("/client/detail_order.html", not_checked=not_checked, order=order[0], space=space)
    
    # check if current time is after the order end time
    now = datetime.datetime.now()
    if not(now > datetime.datetime.fromisoformat(order[0]["end"])):
        return redirect(url_for("history", id=id))
    
    # valid comment and valid time
    ordersDb.execute("UPDATE orders SET comment = ? WHERE id = ? AND username = ?", comment, id, current_username)
    ordersDb.execute("INSERT INTO comments (order_id, username, space, comment, status) VALUES (?, ?, ?, ?, ?)", id, current_username, space["name"], comment, 'show')
    
    # show the comment result in the same page
    order = ordersDb.execute("SELECT * FROM orders WHERE id = ? AND username = ?", id, current_username)[0]
    return redirect(url_for("history", id=id))


# server side
@app.route("/server_login", methods=["GET", "POST"])
def server_login():
    if (request.method == "GET"):
        # if GET server_login, the page only shows when admin doesn't login. otherwise, default page is news list
        if not(session.get("staff_login")):
            return render_template("/server/server_login.html")
        
        return redirect("/server_news")
    
    # POST
    # try login
    staff_login_username = request.form.get("username")
    staff_login_password = request.form.get("password")

    staff = usersDb.execute("SELECT * FROM users WHERE username = ?", staff_login_username)[0]

    # login success
    if (check_password_hash(staff["password"], staff_login_password)):
        session["staff_login"] = True
        return redirect("/server_news")

    # login fail
    return redirect("/server_login")
    
@app.route("/server_logout", methods=["GET"])
def server_logout():
    del session["staff_login"]
    return redirect("/server_login")

@app.route("/server_news", methods=["GET"])
def server_news():
    if not (session.get("staff_login")):
        return redirect("/server_login")
    
    if (request.method == "GET"):
        # if admin choose a specific news id to view the detail
        if (request.args.get("id")):
            id = request.args.get("id")
            article = articlesDb.execute("SELECT * FROM news WHERE id = ?", id)[0]
            return render_template("/server/server_detail_news.html", article=article)
        
        # normal GET, show a list with all news
        news = articlesDb.execute("SELECT * FROM news ORDER BY date DESC")
        return render_template("/server/server_news.html", news=news)
    
@app.route("/news_update", methods=["POST"])
def news_update():
    if not (session.get("staff_login")):
        return redirect("/server_login")
    
    id = request.form.get("id")
    title = request.form.get("title")
    date = request.form.get("date")
    cover_img = request.form.get("cover")
    content = request.form.get("content")

    # no empty
    if (id.strip() == "") or (title.strip() == "") or (date.strip() == "") or (cover_img.strip() == ""):
        news_update_fail = True
        return render_template("/server/server_detail_news.html", news_update_fail=news_update_fail)
    # check tinymce kit content (textarea)
    check_content = content.replace("<p>", "")
    check_content = check_content.replace("</p>", "")
    check_content = check_content.replace("&nbsp;", "")
    if not (check_content.strip()):
        news_update_fail = True
        return render_template("/server/server_detail_news.html", news_update_fail=news_update_fail)

    # valid update
    articlesDb.execute("UPDATE news SET title = ?, date = ?, cover = ?, content = ? WHERE id = ?", title, date, '/static/'+str(cover_img) , content, id)
    return redirect("/server_news")

@app.route("/delete_news", methods=["GET"])
def delete_news():
    if not (session.get("staff_login")):
        return redirect("/server_login")

    id = request.args.get("id")
    articlesDb.execute("DELETE FROM news WHERE id = ?", id)

    return redirect("/server_news")

@app.route("/post", methods=["GET", "POST"])
def post():
    # only two article types
    categories = ['news', 'events']

    if (request.method == "GET"):
        if not (session.get("staff_login")):
            return redirect("/server_login")
        # show the empty form for post a new article
        return render_template("/server/server_post.html", categories=categories)
    
    # POST
    title = request.form.get("title")
    date = request.form.get("date")
    cover_img = request.form.get("cover")
    content = request.form.get("content")
    category = request.form.get("category")

    # no empty
    if (title.strip() == "") or (date.strip() == "") or (cover_img.strip() == "") or (category.strip() == ""):
        post_fail = True
        return render_template("/server/server_post.html", post_fail=post_fail, categories=categories)
    # check tinymce kit content (textarea)
    check_content = content.replace("<p>", "")
    check_content = check_content.replace("</p>", "")
    check_content = check_content.replace("&nbsp;", "")
    if not (check_content.strip()):
        post_fail = True
        return render_template("/server/server_post.html", post_fail=post_fail, categories=categories)

    # valid new post for news
    if (category == "news"):
        articlesDb.execute("INSERT INTO news (title, date, content, cover, attachment) VALUES (?, ?, ?, ?, ?)", title, date, content, '/static/'+str(cover_img), '/static/'+str(cover_img))
        return redirect("/server_news")

    # valid new post for events
    if (category == "events"):
        month = calendar.month_abbr[int(datetime.datetime.strptime(date, '%Y-%m-%d').month)].upper()
        day = datetime.datetime.strptime(date, '%Y-%m-%d').day
        articlesDb.execute("INSERT INTO events (title, date, month, day, content, cover, attachment) VALUES (?, ?, ?, ?, ?, ?, ?)", title, date, month, day, content, '/static/'+str(cover_img), '/static/'+str(cover_img))
        return redirect("/server_events")

@app.route("/server_events", methods=["GET", "POST"])
def server_events():
    if not (session.get("staff_login")):
        return redirect("/server_login")
    
    if (request.method == "GET"):
        # if admin choose a specific event id to view the detail
        if (request.args.get("id")):
            id = request.args.get("id")
            article = articlesDb.execute("SELECT * FROM events WHERE id = ?", id)[0]
            return render_template("/server/server_detail_events.html", article=article)
        
        # normal GET, show a list with all events
        events = articlesDb.execute("SELECT * FROM events ORDER BY date DESC")
        return render_template("/server/server_events.html", events=events)
    
@app.route("/events_update", methods=["POST"])
def events_update():
    if not (session.get("staff_login")):
        return redirect("/server_login")
    
    id = request.form.get("id")
    title = request.form.get("title")
    date = request.form.get("date")
    cover_img = request.form.get("cover")
    content = request.form.get("content")

    # not empty
    if (id.strip() == "") or (title.strip() == "") or (date.strip() == "") or (cover_img.strip() == ""):
        events_update_fail = True
        return render_template("/server/server_detail_events.html", events_update_fail=events_update_fail)
    # check tinymce kit content (textarea)
    check_content = content.replace("<p>", "")
    check_content = check_content.replace("</p>", "")
    check_content = check_content.replace("&nbsp;", "")
    if not (check_content.strip()):
        return render_template("/server/server_detail_events.html")

    # valid update
    month = calendar.month_abbr[int(datetime.datetime.strptime(date, '%Y-%m-%d').month)].upper()
    day = datetime.datetime.strptime(date, '%Y-%m-%d').day
    articlesDb.execute("UPDATE events SET title = ?, date = ?, month = ?, day = ?, cover = ?, content = ? WHERE id = ?", title, date, month, day, '/static/'+str(cover_img), content, id)
    return redirect("/server_events")

@app.route("/delete_events", methods=["GET"])
def delete_events():
    if not (session.get("staff_login")):
        return redirect("/server_login")

    id = request.args.get("id")
    articlesDb.execute("DELETE FROM events WHERE id = ?", id)

    return redirect("/server_events")

@app.route("/server_rooms", methods=["GET"])
def server_rooms():
    if not (session.get("staff_login")):
        return redirect("/server_login")
    
    if (request.method == "GET"):
        # if admin choose a specific room id to view the detail
        if (request.args.get("id")):
            id = request.args.get("id")
            room = spacesDb.execute("SELECT * FROM spaces WHERE id = ?", id)[0]
            equipment = spacesDb.execute("SELECT equipments FROM spaces WHERE id = ?", id)[0]["equipments"]
            # make equipment from database covert into an array, to make template accesses data easier
            equipments = equipment.split(', ')
            return render_template("/server/server_detail_rooms.html", room=room, equipments=equipments)
        
        # normal GET, show a list with all rooms
        rooms = spacesDb.execute("SELECT * FROM spaces ORDER BY location DESC")
        return render_template("/server/server_rooms.html", rooms=rooms)

@app.route("/new_room", methods=["GET", "POST"])
def new_room():
    if not (session.get("staff_login")):
        return redirect("/server_login")
    
    if (request.method == "GET"):
        # show a new empty form to create a new room
        return render_template("/server/server_new_room.html")
    
    # POST
    name = request.form.get("name")
    location = request.form.get("location")
    address = request.form.get("address")
    capacity = request.form.get("capacity")
    price = request.form.get("price")
    cover_img = request.form.get("cover")
    equipments = []

    # no empty
    if (name.strip() == "") or (location.strip() == "") or (address.strip() == "") or (capacity.strip() == "") or (price.strip() == "") or (cover_img.strip() == ""):
        add_room_fail = True
        return render_template("/server/server_new_room.html", add_room_fail=add_room_fail)
    
    # get checkbox value and push to the array
    equipments.extend((request.form.get("ProjectorAndTouchscreen"), request.form.get("Wi-Fi"), request.form.get("A/C"), request.form.get("TeaAndCoffee"), request.form.get("BasicStationary"), request.form.get("A4Paper"), request.form.get("restroom")))
    # make the array covert into a pure string, to make create database data easier
    equipment = ', '.join(str(equipment) for equipment in equipments)

    spaces_names = spacesDb.execute("SELECT name FROM spaces")
    # if any room exists in database, then need to check if name repeated
    if (len(spaces_names) > 0):
        for space_name in spaces_names:
            if name == space_name["name"]:
                space_name_repeat = True
                return render_template("/server/server_new_room.html", space_name_repeat=space_name_repeat)

    # valid new room. no name repeated or the database is empty
    spacesDb.execute("INSERT INTO spaces (name, location, address, capacity, price, equipments, img) VALUES (?, ?, ?, ?, ?, ?, ?)", name, location, address, int(capacity), int(price), equipment, '/static/'+str(cover_img))
    return redirect("/server_rooms")

@app.route("/rooms_update", methods=["POST"])
def rooms_update():
    if not (session.get("staff_login")):
        return redirect("/server_login")
    
    id = request.form.get("id")
    name = request.form.get("name")
    location = request.form.get("location")
    address = request.form.get("address")
    capacity = request.form.get("capacity")
    price = request.form.get("price")
    cover_img = request.form.get("cover")
    equipments = []

    # not empty
    if (id.strip() == "") or (name.strip() == "") or (location.strip() == "") or (address.strip() == "") or (capacity.strip() == "") or (price.strip() == "") or (cover_img.strip() == ""):
        room_update_fail = True
        return render_template("/server/server_detail_rooms.html", room_update_fail=room_update_fail)
    # get checkbox value and push to the array
    equipments.extend((request.form.get("ProjectorAndTouchscreen"), request.form.get("Wi-Fi"), request.form.get("A/C"), request.form.get("TeaAndCoffee"), request.form.get("BasicStationary"), request.form.get("A4Paper"), request.form.get("restroom")))
    # make the array covert into a pure string, to make create database data easier
    equipment = ', '.join(str(equipment) for equipment in equipments)

    # name cannot be repeated
    spaces_names = spacesDb.execute("SELECT name FROM spaces")
    # if any room exists in database, then need to check if name repeated
    if (len(spaces_names) > 0):
        for space_name in spaces_names:
            if name == space_name["name"]:
                space_name_repeat = True
                return render_template("/server/server_detail_rooms.html", space_name_repeat=space_name_repeat)

    # valid update
    spacesDb.execute("UPDATE spaces SET name = ?, location = ?, address = ?, capacity = ?, price = ?, equipments = ?, img = ? WHERE id = ?", name, location, address, int(capacity), int(price), equipment, '/static/'+str(cover_img), id)
    return redirect("/server_rooms")

@app.route("/delete_rooms", methods=["GET"])
def delete_rooms():
    if not (session.get("staff_login")):
        return redirect("/server_login")

    id = request.args.get("id")
    spacesDb.execute("DELETE FROM spaces WHERE id = ?", id)

    return redirect("/server_rooms")

@app.route("/server_orders", methods=["GET"])
def server_orders():
    if not (session.get("staff_login")):
        return redirect("/server_login")
    
    if (request.method == "GET"):
        # if admin choose a specific order id to view the detail
        if (request.args.get("id")):
            id = request.args.get("id")
            order = ordersDb.execute("SELECT * FROM orders WHERE id = ?", id)[0]
            return render_template("/server/server_detail_orders.html", order=order)
        
        # normal GET, show a list with all orders
        orders = ordersDb.execute("SELECT * FROM orders ORDER BY application_date DESC")
        return render_template("/server/server_orders.html", orders=orders)
    
@app.route("/orders_update", methods=["POST"])
def orders_update():
    if not (session.get("staff_login")):
        return redirect("/server_login")
    
    id = request.form.get("id")
    username = request.form.get("username")
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    start = request.form.get("start")
    end = request.form.get("end")
    note = request.form.get("note")

    # no empty
    if (id.strip() == "") or (username.strip() == "") or (name.strip() == "") or (email.strip() == "") or ("@" not in email) or (phone.strip() == "") or (start.strip() == "") or (end.strip() == ""):
        order_update_fail = True
        return render_template("/server/server_detail_orders.html", order_update_fail=order_update_fail)
    
    # check the order current status (canceled or not) and the current time
    status = ordersDb.execute("SELECT status FROM orders WHERE id = ?", id)[0]["status"]
    # all time information is UTC+8 (server timezone), no need to switch
    now = datetime.datetime.now()
    start = datetime.datetime.fromisoformat(start)
    end = datetime.datetime.fromisoformat(end)

    # if has been canceled or current time is after the order start time or it's not before over than 48 hours, then the order cannot be canceled (repeatedly).
    if (status == 'Canceled') or (now > start) or ((now + datetime.timedelta(hours=48)) >= start):
        invalid_update = True
        return render_template("/server/server_detail_orders.html", invalid_update=invalid_update)
    
    # valid canceled request
    ordersDb.execute("UPDATE orders SET email = ?, phone = ?, name = ? WHERE id = ? AND username = ? AND start = ? AND end = ? AND note = ?", email, phone, name, id, username, start, end, note)
    return redirect("/server_orders")

@app.route("/delete_orders", methods=["GET"]) # only use for spam orders
def delete_orders():
    if not (session.get("staff_login")):
        return redirect("/server_login")

    id = request.args.get("id")
    ordersDb.execute("DELETE FROM orders WHERE id = ?", id)

    return redirect("/server_orders")


@app.route("/server_comments", methods=["GET"])
def server_comments():
    if not (session.get("staff_login")):
        return redirect("/server_login")
    
    if (request.method == "GET"):
        # if admin choose a specific comment id to view the detail
        if (request.args.get("id")):
            id = request.args.get("id")
            comment = ordersDb.execute("SELECT * FROM comments WHERE id = ?", id)[0]
            return render_template("/server/server_detail_comments.html", comment=comment)
        
        # normal GET, show a list with all comments
        comments = ordersDb.execute("SELECT * FROM comments ORDER BY id")
        return render_template("/server/server_comments.html", comments=comments)

@app.route("/comment_update", methods=["POST"]) # only use for if show the comment or not, if there's irrational opinion
def comment_update():
    id = request.form.get("id")
    order_id = request.form.get("order_id")
    username = request.form.get("username")
    space = request.form.get("space")
    status = request.form.get("status")

    ordersDb.execute("UPDATE comments SET status = ? WHERE id = ? AND order_id = ? AND username = ? AND space = ?", status, id, order_id, username, space)
    return redirect("/server_comments")


@app.route("/delete_comments", methods=["GET"]) # only use for spam order
def delete_comments():
    if not (session.get("staff_login")):
        return redirect("/server_login")

    id = request.args.get("id")
    ordersDb.execute("DELETE FROM comments WHERE id = ?", id)

    return redirect("/server_comments")
