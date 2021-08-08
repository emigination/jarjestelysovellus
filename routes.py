from flask import Flask, render_template, session, redirect, request
from app import app
import users
import items

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
    name = request.form["name"]
    password = request.form["password"]
    result = users.check_user(name, password)
    if result=='accepted':
        session["name"] = name
        session["id"] = name
        return redirect("/")
    else:
        return render_template("index.html", error=result)

@app.route("/logout")
def logout():
    del session["name"]
    return redirect("/")

@app.route("/create_user")
def create_user():
    return render_template("create_user.html")

@app.route("/register",methods=["POST"])
def register():
    name = request.form["name"]
    password = request.form["password"]
    if users.create_user(name, password):
        session["name"] = name
        return redirect("/")
    else:
        return render_template("create_user.html", error=1)

@app.route("/add_item")
def add_item():
    return render_template("add_item.html")

@app.route("/new_item",methods=["POST"])
def new_item():
    name = request.form["name"]
    location = request.form["location"]
    if items.new_item(name, location):
        return redirect("/")
    else:
        return render_template("add_item.html", error=1)

@app.route("/search_item")
def search_item():
    return render_template("search_item.html")

@app.route("/fetch_item",methods=["POST"])
def fetch_item():
    name = request.form["name"]
    result = items.find_by_name(name)
    if result:
        return render_template("search_results.html", item=result)
    else:
        return render_template("search_item.html", error=1)

@app.route("/fetch_all_items",methods=["POST"])
def fetch_all_items():
    result = items.fetch_all_items()
    if result:
        return render_template("search_results.html", item=result)
    else:
        return render_template("search_item.html", error=1)

