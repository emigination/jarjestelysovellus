from flask import session
from db import db
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import exc


def create_user(name, password):
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (name,password) VALUES (:name,:password)"
        db.session.execute(sql, {"name": name, "password": hash_value})
        db.session.commit()
    except Exception as e:
        return False
    user = fetch_user(name)
    session["user_id"] = user.id
    return True


def check_user(name, password):
    user = fetch_user(name)
    if not user:
        return 1
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            return 0
        else:
            return 1


def fetch_user(name):
    sql = "SELECT id, password FROM users WHERE name=:name"
    return db.session.execute(sql, {"name": name}).fetchone()
