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
        return render_template("success.html", title="Luo uusi käyttäjä", action="Käyttäjätunnuksen luonti")
    else:
        return render_template("create_user.html", error="Käyttäjätunnus on jo käytössä!")


@app.route("/add_item")
def add_item():
    return render_template("add_item.html")


@app.route("/new_item", methods=["POST"])
def new_item():
    name = request.form["name"]
    parent_item = request.form["parent_item"]
    location = request.form["location"]
    dimensions = request.form["dimensions"]
    year = request.form["year"]
    tags = request.form["tags"]
    error = items.check_input(
        name, parent_item, location, dimensions, year, tags)
    if error:
        return render_template("add_item.html", error=error)
    elif items.new_item(name, parent_item, location, dimensions, year, tags):
        return render_template("success.html", title="Lisää tavara", action="Tavaran lisäys")
    else:
        return render_template("add_item.html", error='Epäonnistui :(')


@app.route("/search_item")
def search_item():
    no_of_items = items.get_no_of_items()
    return render_template("search_item.html", no_of_items=no_of_items)


@app.route("/fetch_item")
def fetch_item():
    name = request.args["name"]
    result = items.find_by_name(name)
    if result:
        tags = items.get_item_tags(result[0].id)
        location = items.find_by_id(result[0].location_id).name
        return render_template("search_results.html", items=result, tags=[tags], locations=[location])
    else:
        no_of_items = items.get_no_of_items()
        return render_template("search_item.html", no_of_items=no_of_items, error=1)


@app.route("/fetch_by_tag")
def fetch_by_tag():
    tag = request.args["tag"]
    result = items.find_by_tag(tag)
    if result:
        (locations, tags) = items.get_tags_locations(result)
        return render_template("search_results.html", items=result, tags=tags, locations=locations)
    else:
        no_of_items = items.get_no_of_items()
        return render_template("search_item.html", no_of_items=no_of_items, error=1)


@app.route("/fetch_all_items")
def fetch_all_items():
    result = items.fetch_all_items()
    if result:
        (locations, tags) = items.get_tags_locations(result)
        return render_template("search_results.html", items=result, tags=tags, locations=locations)
    else:
        no_of_items = items.get_no_of_items()
        return render_template("search_item.html", no_of_items=no_of_items, error=1)


@app.route("/edit_item/<int:id>")
def edit_item(id):
    (item, tags, location) = items.get_all_by_id(id)
    return render_template("edit_item.html", item=item, location=location, tag_string=tags)


@app.route("/update_item/<int:id>", methods=["POST"])
def update_item(id):
    name = request.form["name"]
    parent_item = request.form["parent_item"]
    location = request.form["location"]
    dimensions = request.form["dimensions"]
    year = request.form["year"]
    tags = request.form["tags"]
    error = items.check_input(
        name, parent_item, location, dimensions, year, tags, id)
    if not error:
        if items.edit(id, name, parent_item, location, dimensions, year, tags):
            return render_template("success.html", title="Muokkaa tavaraa", action="Tavaran muokkaus")
        else:
            error = 'Epäonnistui :('
    (item, tagstring, location) = items.get_all_by_id(id)
    return render_template("edit_item.html", item=item, location=location, tag_string=tagstring, error=error)


@app.route("/delete_item/<int:id>")
def delete_item(id):
    item = items.find_by_id(id)
    return render_template("delete_item.html", item=item)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    if items.delete_item(id):
        return render_template("success.html", title="Poista tavara", action="Tavaran poistaminen")
    no_of_items = items.get_no_of_items()
    return render_template("search_item.html", no_of_items=no_of_items)
