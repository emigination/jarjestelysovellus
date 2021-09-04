from os import get_terminal_size
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
        return False
    return True


def edit(id, name, parent_item, location, dimensions, year, tags):
    if not user_is_owner(id):
        return False
    if year.isnumeric():
        year = int(year)
    else:
        year = 0
    if parent_item:
        parent_id = find_by_name(parent_item)[0].id
    else:
        parent_id = None
    try:
        sql = "UPDATE items SET name=:name, location_id=:location_id, location=:location, dimensions=:dimensions, year=:year WHERE id=:id"
        db.session.execute(
            sql, {"id": id, "name": name, "location_id": parent_id, "location": location, "dimensions": dimensions, "year": year})
        sql = "DELETE FROM tags WHERE item_id=:id"
        db.session.execute(sql, {"id": id})
        if tags:
            taglist = tags.split(' ')
            for tag in taglist:
                sql = "INSERT INTO tags (tag, item_id) VALUES (:tag, :item_id)"
                db.session.execute(sql, {"tag": tag, "item_id": id})
        db.session.commit()
    except Exception as e:
        return False
    return True


def find_by_id(id):
    sql = "SELECT i.id, i.name, i.location_id, i.location, i.dimensions, i.year FROM items i, owners o WHERE i.id=o.item_id AND i.id=:id AND o.user_id=:owner_id"
    item = db.session.execute(
        sql, {"id": id, "owner_id": session["user_id"]}).fetchone()
    return item


def find_by_name(name):
    sql = "SELECT i.id, i.name, i.location_id, i.location, i.dimensions, i.year, u.name AS owner_name FROM items i " +\
            "LEFT JOIN owners o ON i.id=o.item_id LEFT JOIN users u ON o.user_id=u.id LEFT JOIN viewers v ON i.id=v.item_id " +\
                "WHERE i.name=:name AND (o.user_id=:user_id OR v.user_id=:user_id)"
    items = db.session.execute(
        sql, {"name": name, "user_id": session["user_id"]}).fetchall()
    return items


def find_by_tag(tag):
    sql = "SELECT i.id, i.name, i.location_id, i.location, i.dimensions, i.year, u.name AS owner_name FROM items i " +\
            "LEFT JOIN owners o ON i.id=o.item_id LEFT JOIN users u ON o.user_id=u.id LEFT JOIN viewers v ON i.id=v.item_id LEFT JOIN tags t ON i.id=t.item_id " +\
                "WHERE t.tag=:tag AND (o.user_id=:user_id OR v.user_id=:user_id) ORDER BY i.name"
    items = db.session.execute(
        sql, {"tag": tag, "user_id": session["user_id"]}).fetchall()
    return items


def find_by_container(container_id):
    sql = "SELECT i.id, i.name, i.location_id, i.location, i.dimensions, i.year, u.name AS owner_name FROM items i " +\
            "LEFT JOIN owners o ON i.id=o.item_id LEFT JOIN users u ON o.user_id=u.id LEFT JOIN viewers v ON i.id=v.item_id  " +\
                "WHERE i.location_id=:container_id AND (o.user_id=:user_id OR v.user_id=:user_id) ORDER BY i.name"
    items = db.session.execute(
        sql, {"container_id": container_id, "user_id": session["user_id"]}).fetchall()
    return items


def fetch_all_items():
    sql = "SELECT i.id, i.name, i.location_id, i.location, i.dimensions, i.year, u.name AS owner_name FROM items i " +\
            "LEFT JOIN owners o ON i.id=o.item_id LEFT JOIN users u ON o.user_id=u.id LEFT JOIN viewers v ON i.id=v.item_id  " +\
                "WHERE o.user_id=:user_id OR v.user_id=:user_id ORDER BY i.name"
    items = db.session.execute(
        sql, {"user_id": session["user_id"]}).fetchall()
    return items


def get_name(id):
    sql = "SELECT name FROM items WHERE id=:id"
    item = db.session.execute(sql, {"id": id}).fetchone()
    return item.name


def get_item_tags(id):
    sql = "SELECT id, tag FROM tags WHERE item_id=:item_id ORDER BY tag"
    tags = db.session.execute(sql, {"item_id": id}).fetchall()
    return tags


def get_no_of_items():
    sql = "SELECT COUNT(*) FROM items i, owners o WHERE i.id=o.item_id AND o.user_id=:owner_id"
    own = db.session.execute(
        sql, {"owner_id": session["user_id"]}).fetchone()[0]
    sql = "SELECT COUNT(*) FROM items i, viewers v WHERE i.id=v.item_id AND v.user_id=:user_id"
    viewable = db.session.execute(
        sql, {"user_id": session["user_id"]}).fetchone()[0]
    return (own, viewable)


def get_tags_locations_contents(result):
    tags = []
    locations = []
    contents = []
    for item in result:
        tags.append(get_item_tags(item.id))
        if item.location_id:
            location_name = get_name(item.location_id)
            locations.append(location_name)
        else:
            locations.append('')
        no_of_contents = get_no_of_contents(item.id)
        contents.append(no_of_contents)
    return (locations, tags, contents)


def get_no_of_contents(id):
    sql = "SELECT COUNT(*) FROM items i WHERE i.location_id=:id"
    number = db.session.execute(
        sql, {"id": id}).fetchone()[0]
    return number


def get_all_by_id(id):
    item = find_by_id(id)
    if item.location_id:
        location = get_name(item.location_id)
    else:
        location = ''
    tagstring = ''
    for tag in get_item_tags(id):
        tagstring += tag.tag + ' '
    return (item, tagstring, location)


def check_input(name, parent_item, location, dimensions, year, tags, id=None):
    if len(name) > 100 or len(name) < 1:
        return 'Nimen pituuden tulee olla 1-100 merkkiä.'
    else:
        samenameitem = find_by_name(name)
    if samenameitem and ((id and samenameitem[0].id != id) or not id):
        return 'Sinulla on jo samanniminen tavara!'
    if not (id and location==get_all_by_id(id)[2]) and (len(parent_item) > 100 or (parent_item and not find_by_name(parent_item))):
        return 'Sisältävää tavaraa ei löydy. Tarkista, että kirjoitit sen nimen oikein.'
    if len(location) > 100:
        return 'Sijainnin kuvaus on liian pitkä! Pituus saa olla enintään 100 merkkiä.'
    if len(dimensions) > 100:
        return 'Mittojen kuvaus on liian pitkä! Pituus saa olla enintään 100 merkkiä.'
    if year and (not year.isnumeric() or int(year) > 9999 or int(year) < 1):
        return 'Vuoden tulee olla väliltä 1-9999'
    if len(tags) > 100:
        return 'Tägien yhteispituus saa olla enintään 100 merkkiä.'
    return


def delete_item(id):
    if not user_is_owner(id):
        return False
    try:
        sql = "UPDATE items SET location_id=NULL where location_id=:id"
        db.session.execute(sql, {"id": id})
        sql = "DELETE FROM items WHERE id=:id"
        db.session.execute(sql, {"id": id})
        db.session.commit()
    except Exception as e:
        return False
    return True


def add_viewer(item_id, user_id):
    if not user_is_owner(item_id):
        return False
    sql = "SELECT COUNT(*) FROM viewers WHERE item_id=:item_id AND user_id=:user_id"
    already_exists = db.session.execute(
        sql, {"item_id": item_id, "user_id": user_id}).fetchone()[0]
    if already_exists:
        return 'Käyttäjällä on jo katseluoikeus tavaraan!'
    sql = "SELECT COUNT(*) FROM owners WHERE item_id=:item_id AND user_id=:user_id"
    already_owner= db.session.execute(
        sql, {"item_id": item_id, "user_id": user_id}).fetchone()[0]
    if already_owner:
        return 'Käyttäjä on jo tavaran omistaja, joten et voi tehdä hänestä katselijaa!'
    sql = "INSERT INTO viewers (item_id,user_id) VALUES (:item_id,:user_id)"
    try:
        db.session.execute(sql, {"item_id": item_id, "user_id": user_id})
        db.session.commit()
    except Exception as e:
        return 'Epäonnistui :('
    return 'success'


def add_owner(item_id, user_id):
    if not user_is_owner(item_id):
        return False
    sql = "SELECT COUNT(*) FROM owners WHERE item_id=:item_id AND user_id=:user_id"
    already_owner= db.session.execute(
        sql, {"item_id": item_id, "user_id": user_id}).fetchone()[0]
    if already_owner:
        return 'Käyttäjä on jo tavaran omistaja!'
    try:
        sql = "INSERT INTO owners (item_id,user_id) VALUES (:item_id,:user_id)"
        db.session.execute(sql, {"item_id": item_id, "user_id": user_id})
        sql = "DELETE FROM viewers WHERE user_id=:user_id AND item_id=:item_id"
        db.session.execute(sql, {"item_id": item_id, "user_id": user_id})
        db.session.commit()
    except Exception as e:
        return 'Epäonnistui :('
    return 'success'

def user_is_owner(item_id):
    sql = "SELECT COUNT(*) FROM owners WHERE item_id=:item_id AND user_id=:user_id"
    is_owner = db.session.execute(
        sql, {"item_id": item_id, "user_id": session["user_id"]}).fetchone()[0]
    if is_owner:
        return True
    return False
