from os import error
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


@app.route("/fetch_by_name")
def fetch_by_name():
    name = request.args["name"]
    result = items.find_by_name(name)
    if result:
        (locations, tags, no_of_contents) = items.get_tags_locations_contents(result)
        return render_template("search_results.html", items=result, tags=[tags], locations=locations, contents=no_of_contents)
    else:
        no_of_items = items.get_no_of_items()
        return render_template("search_item.html", no_of_items=no_of_items, error='Hakemaasi tavaraa ei löydy!')


@app.route("/fetch_by_tag")
def fetch_by_tag():
    tag = request.args["tag"]
    result = items.find_by_tag(tag)
    if result:
        (locations, tags, no_of_contents) = items.get_tags_locations_contents(result)
        return render_template("search_results.html", items=result, tags=tags, locations=locations, contents=no_of_contents)
    else:
        no_of_items = items.get_no_of_items()
        return render_template("search_item.html", no_of_items=no_of_items, error='Tägillä ei löydy yhtään tavara!')


@app.route("/fetch_by_tag_name/<string:tag>")
def fetch_by_tag_name(tag):
    result = items.find_by_tag(tag)
    if result:
        (locations, tags, no_of_contents) = items.get_tags_locations_contents(result)
        return render_template("search_results.html", items=result, tags=tags, locations=locations, contents=no_of_contents)
    else:
        no_of_items = items.get_no_of_items()
        return render_template("search_item.html", no_of_items=no_of_items, error='Tägillä ei löydy yhtään tavara!')


@app.route("/fetch_contents_by_name")
def fetch_contents_by_name():
    container = items.find_by_name(request.args["container"])
    if not container:
        error = 'Tavaraa, jonka sisältöä haet, ei löydy!'
    else:
        container_id = container[0].id
        result = items.find_by_container(container_id)
        if result:
            (locations, tags, no_of_contents) = items.get_tags_locations_contents(result)
            return render_template("search_results.html", items=result, tags=tags, locations=locations, contents=no_of_contents)
        error = f'"{container[0].name}" ei sisällä yhtään tavaraa.'
    no_of_items = items.get_no_of_items()
    return render_template("search_item.html", no_of_items=no_of_items, error=error)


@app.route("/fetch_contents/<int:id>")
def fetch_contents(id):
    result = items.find_by_container(id)
    if result:
        (locations, tags, no_of_contents) = items.get_tags_locations_contents(result)
        return render_template("search_results.html", items=result, tags=tags, locations=locations, contents=no_of_contents)
    no_of_items = items.get_no_of_items()
    return render_template("search_item.html", no_of_items=no_of_items, error='Haettua tavaraa ei löytynyt!')


@app.route("/fetch_all_items")
def fetch_all_items():
    result = items.fetch_all_items()
    if result:
        (locations, tags, no_of_contents) = items.get_tags_locations_contents(result)
        return render_template("search_results.html", items=result, tags=tags, locations=locations, contents=no_of_contents)
    else:
        no_of_items = items.get_no_of_items()
        return render_template("search_item.html", no_of_items=no_of_items, error='Sinulla ei ole yhtään tavaraa')


@app.route("/edit_item/<int:id>")
def edit_item(id):
    (item, tagstring, location) = items.get_all_by_id(id)
    return render_template("edit_item.html", item=item, location=location, tag_string=tagstring)


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


@app.route("/add_viewer/<int:id>")
def add_viewer(id):
    item = items.find_by_id(id)
    if item:
        return render_template("add_viewer.html", item_id=id, item_name=item.name)
    return render_template("add_viewer.html", item_id=id, item_name=item.name, error='Epäonnistui :(')


@app.route("/new_viewer", methods=["POST"])
def new_viewer():
    username = request.form["username"]
    item_name = request.form["item_name"]
    item_id = request.form["item_id"]
    user = users.fetch_user(username)
    if not user:
        error = f'Käyttäjää {username} ei löydy!'
    else:
        result = items.add_viewer(item_id, user.id)
        if result == 'success':
            return render_template("success.html", title="Lisää katseluoikeus", action="Katseluoikeuden lisääminen")
        error = result
    return render_template("add_viewer.html", item_id=item_id, item_name=item_name, error=error)


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
