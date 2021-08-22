from flask import session
from db import db


def new_item(name, parent_item=None, location=None, dimensions=None, year=None, tags=None):
    if year.isnumeric():
        year = int(year)
    else:
        year = 0
    if parent_item:
        parent_id = find_by_name(parent_item)[0].id
    else:
        parent_id = None
    try:
        sql = "INSERT INTO items (name,location_id,location,dimensions,year) VALUES (:name,:location_id,:location,:dimensions,:year) RETURNING id"
        item_id = db.session.execute(sql, {"name": name, "location_id": parent_id, "location": location,
                                           "dimensions": dimensions, "year": year}).fetchone().id
        sql = "INSERT INTO owners (item_id, user_id) VALUES (:item_id,:user_id)"
        db.session.execute(
            sql, {"item_id": item_id, "user_id": session["user_id"]})
        if tags:
            taglist = tags.split(' ')
            for tag in taglist:
                sql = "INSERT INTO tags (tag, item_id) VALUES (:tag, :item_id)"
                db.session.execute(sql, {"tag": tag, "item_id": item_id})
        db.session.commit()
    except Exception as e:
        print('virhe:', e)
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
    sql = "SELECT i.id, i.name, i.location_id, i.location, i.dimensions, i.year FROM items i, owners o WHERE i.id=o.item_id AND i.name=:name AND o.user_id=:owner_id"
    items = db.session.execute(
        sql, {"name": name, "owner_id": session["user_id"]}).fetchall()
    return items


def find_by_id(id):
    sql = "SELECT i.id, i.name, i.location_id, i.location, i.dimensions, i.year FROM items i, owners o WHERE i.id=o.item_id AND i.id=:id AND o.user_id=:owner_id"
    item = db.session.execute(
        sql, {"id": id, "owner_id": session["user_id"]}).fetchone()
    return item


def find_by_tag(tag):
    sql = "SELECT i.id, i.name, i.location_id, i.location, i.dimensions, i.year FROM items i, owners o, tags t WHERE i.id=o.item_id AND i.id=t.item_id AND t.tag=:tag AND o.user_id=:owner_id"
    items = db.session.execute(
        sql, {"tag": tag, "owner_id": session["user_id"]}).fetchall()
    return items


def fetch_all_items():
    sql = "SELECT i.id, i.name, i.location_id, i.location, i.dimensions, i.year FROM items i, owners o WHERE i.id=o.item_id AND o.user_id=:owner_id"
    items = db.session.execute(
        sql, {"owner_id": session["user_id"]}).fetchall()
    return items


def get_item_tags(id):
    sql = "SELECT tag FROM tags WHERE item_id=:item_id"
    tags = db.session.execute(sql, {"item_id": id}).fetchall()
    print(tags)
    return tags


def get_no_of_items():
    sql = "SELECT COUNT(*) FROM items i, owners o WHERE i.id=o.item_id AND o.user_id=:owner_id"
    number = db.session.execute(
        sql, {"owner_id": session["user_id"]}).fetchone()[0]
    return number


def get_tags_locations(result):
    tags = []
    locations = []
    for item in result:
        tags.append(get_item_tags(item.id))
        location = find_by_id(item.location_id)
        if location:
            locations.append(location.name)
        else:
            locations.append('')
    return (tags, locations)
