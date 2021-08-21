from flask import session
from db import db


def new_item(name, parent_item, location, dimensions, year, tags):
    try:
        parent_id = find_by_name(parent_item).id
        sql = "INSERT INTO items (name,location_id,location,dimensions,year) VALUES (:name,:parent_id,:location,:dimensions,:year)"
        db.session.execute(sql, {"name": name, "location_id": parent_id, "location": location,
                                 "dimensions": dimensions, "year": year})
        item_id = find_by_name(name).id
        sql = "INSERT INTO owners (item_id, user_id) VALUES (:item_id,:user_id)"
        db.session.execute(
            sql, {"item_id": item_id, "user_id": session["user_id"]})
        taglist = tags.split(' ')
        for tag in taglist:
            sql = "INSERT INTO tags (tag, item_id) VALUES (:tag, :item_id)"
            db.session.execute(sql, {"tag": tag, "item_id": item_id})
        db.session.commit()
    except Exception as e:
        return False
    return True


def edit(id, name, location):
    try:
        sql = "UPDATE items SET name=:name, location=:location WHERE id=:id AND owner_id=:owner_id"
        db.session.execute(
            sql, {"id": id, "name": name, "location": location, "owner_id": session["user_id"]})
        db.session.commit()
    except Exception as e:
        return False
    return True


def find_by_name(name):
    sql = "SELECT id, name, location FROM items WHERE name=:name AND owner_id=:owner_id"
    item = db.session.execute(
        sql, {"name": name, "owner_id": session["user_id"]}).fetchall()
    return item


def find_by_id(id):
    sql = "SELECT id, name, location FROM items WHERE id=:id AND owner_id=:owner_id"
    item = db.session.execute(
        sql, {"id": id, "owner_id": session["user_id"]}).fetchone()
    return item


def fetch_all_items():
    sql = "SELECT id, name, location FROM items WHERE owner_id=:owner_id"
    items = db.session.execute(
        sql, {"owner_id": session["user_id"]}).fetchall()
    return items
