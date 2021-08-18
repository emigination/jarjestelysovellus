from flask import Flask, render_template, session, redirect, request
from app import app
import users
import items


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    name = request.form["name"]
    password = request.form["password"]
    if len(name) > 50 or len(password) > 50:
        error = 1
    else:
        error = users.check_user(name, password)
    if not error:
        session["name"] = name
        session["user_id"] = users.fetch_user(name).id
        return redirect("/")
    else:
        return render_template("index.html", error=1)


@app.route("/logout")
def logout():
    del session["name"]
    return redirect("/")


@app.route("/create_user")
def create_user():
    return render_template("create_user.html")


@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    password = request.form["password"]
    if len(name) < 2 or len(name) > 50:
        return render_template("create_user.html", error="Käyttäjätunnuksen pituuden tulee olla 2–50 merkkiä!")
    if len(password) < 6 or len(password) > 50:
        return render_template("create_user.html", error="Salasanan pituuden tulee olla 6–50 merkkiä!")
    if users.create_user(name, password):
        session["name"] = name
        session["user_id"] = users.fetch_user(name).id
        return redirect("/")
    else:
        return render_template("create_user.html", error="Käyttäjätunnus on jo käytössä!")


@app.route("/add_item")
def add_item():
    return render_template("add_item.html")


@app.route("/new_item", methods=["POST"])
def new_item():
    name = request.form["name"]
    location = request.form["location"]
    if len(name) > 100:
        error = 'Nimi on liian pitkä! Pituus saa olla enintään 100 merkkiä.'
    elif len(location) > 100:
        error = 'Sijainnin kuvaus on liian pitkä! Pituus saa olla enintään 100 merkkiä.'
    elif items.new_item(name, location):
        return redirect("/")
    else:
        error = 'Epäonnistui :('
    return render_template("add_item.html", error=error)


@app.route("/search_item")
def search_item():
    return render_template("search_item.html")


@app.route("/fetch_item")
def fetch_item():
    name = request.args["name"]
    result = items.find_by_name(name)
    if result:
        return render_template("search_results.html", items=result)
    else:
        return render_template("search_item.html", error=1)


@app.route("/fetch_all_items")
def fetch_all_items():
    result = items.fetch_all_items()
    if result:
        return render_template("search_results.html", items=result)
    else:
        return render_template("search_item.html", error=1)


@app.route("/edit_item/<int:id>")
def edit_item(id):
    item = items.find_by_id(id)
    return render_template("edit_item.html", item=item)


@app.route("/update_item/<int:id>", methods=["POST"], )
def update_item(id):
    name = request.form["name"]
    location = request.form["location"]
    if len(name) > 100:
        error = 'Nimi on liian pitkä! Pituus saa olla enintään 100 merkkiä.'
    elif len(location) > 100:
        error = 'Sijainnin kuvaus on liian pitkä! Pituus saa olla enintään 100 merkkiä.'
    elif items.edit(id, name, location):
        return redirect("/")
    else:
        error = 'Epäonnistui :('
    item = items.find_by_id(id)
    return render_template("edit_item.html", item=item, error=error)