from flask import session
from db import db

def new_item(name, location):
    try:
        sql = "INSERT INTO items (name,location,owner_id) VALUES (:name,:location,:owner_id)"
        db.session.execute(sql, {"name":name, "location":location, "owner_id":session["user_id"]})
        db.session.commit()
    except Exception as e:
        print(e)
        return False
    return True

def find_by_name(name):
    sql = "SELECT id, name, location FROM items WHERE name=:name AND owner_id=:owner_id"
    item = db.session.execute(sql, {"name":name, "owner_id":session["user_id"]}).fetchall()
    return item

def fetch_all_items():
    sql = "SELECT id, name, location FROM items WHERE owner_id=:owner_id"
    item = db.session.execute(sql, {"owner_id":session["user_id"]}).fetchall()
    return item