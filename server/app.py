#!/usr/bin/env python3
"""
Author: Hunter
Date: 2026-01-03
Version: 1.0
"""

from flask import request, session, jsonify
from sqlalchemy.exc import IntegrityError

from config import create_app, db
from models import User

app = create_app()


@app.get("/")
def home():
    return {"status": "ok"}, 200


@app.post("/signup")
def signup():
    data = request.get_json() or {}

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    password_confirmation = data.get("password_confirmation") or ""

    errors = []
    if not username:
        errors.append("Username is required.")
    if not password:
        errors.append("Password is required.")
    if password != password_confirmation:
        errors.append("Password confirmation must match password.")

    if errors:
        return {"errors": errors}, 422

    try:
        user = User(username=username)
        user.password_hash = password  # hashes + stores
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"errors": ["Username already taken."]}, 422
    except ValueError as e:
        db.session.rollback()
        return {"errors": [str(e)]}, 422

    session["user_id"] = user.id
    return user.to_dict(), 201


@app.post("/login")
def login():
    data = request.get_json() or {}

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter(User.username == username).first()

    if not user or not user.authenticate(password):
        return {"errors": ["Invalid username or password."]}, 401

    session["user_id"] = user.id
    return user.to_dict(), 200


@app.get("/check_session")
def check_session():
    user_id = session.get("user_id")
    if not user_id:
        return {}, 401

    user = User.query.get(user_id)
    if not user:
        session.pop("user_id", None)
        return {}, 401

    return user.to_dict(), 200


@app.delete("/logout")
def logout():
    session.pop("user_id", None)
    return {}, 200


if __name__ == "__main__":
    app.run(port=5555, debug=True)
