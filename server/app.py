#!/usr/bin/env python3
"""
Author: Hunter
Date: 2026-01-03
Version: 1.0
"""

from flask import request, session
from sqlalchemy.exc import IntegrityError

from config import create_app, db
from models import User, Note

# Application factory keeps config, extensions, and app setup cleanly separated
app = create_app()


def current_user():
    # Centralized session-based user lookup to avoid duplication
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


@app.get("/")
def home():
    # Simple health check endpoint
    return {"status": "ok"}, 200


@app.post("/signup")
def signup():
    data = request.get_json() or {}

    # Normalize inputs early to avoid downstream edge cases
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
        user.password_hash = password  # Triggers model-level hashing/validation
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        # Handles unique constraint violations cleanly
        db.session.rollback()
        return {"errors": ["Username already taken."]}, 422
    except ValueError as e:
        # Catches model validation errors
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

    # Authentication intentionally fails silently to avoid leaking info
    if not user or not user.authenticate(password):
        return {"errors": ["Invalid username or password."]}, 401

    session["user_id"] = user.id
    return user.to_dict(), 200


@app.get("/check_session")
def check_session():
    # Lightweight session validation for frontend bootstrapping
    user_id = session.get("user_id")
    if not user_id:
        return {}, 401

    user = User.query.get(user_id)
    if not user:
        # Clean up stale session data
        session.pop("user_id", None)
        return {}, 401

    return user.to_dict(), 200


@app.delete("/logout")
def logout():
    # Stateless logout — just clear the session
    session.pop("user_id", None)
    return {}, 200


@app.get("/notes")
def get_notes():
    user = current_user()
    if not user:
        return {"errors": ["Unauthorized"]}, 401

    # Pagination parameters with sane defaults
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    # Guardrails to prevent abuse or accidental overload
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    if per_page > 50:
        per_page = 50

    pagination = (
        Note.query
        .filter(Note.user_id == user.id)
        .order_by(Note.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    items = [n.to_dict() for n in pagination.items]

    return {
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "total_pages": pagination.pages,
        "items": items,
    }, 200


@app.post("/notes")
def create_note():
    user = current_user()
    if not user:
        return {"errors": ["Unauthorized"]}, 401

    data = request.get_json() or {}
    title = data.get("title")
    body = data.get("body")

    try:
        note = Note(title=title, body=body, user_id=user.id)
        db.session.add(note)
        db.session.commit()
    except ValueError as e:
        # Relies on model validation for required fields / constraints
        db.session.rollback()
        return {"errors": [str(e)]}, 422

    return note.to_dict(), 201


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    user = current_user()
    if not user:
        return {"errors": ["Unauthorized"]}, 401

    # Enforces ownership at the query level
    note = Note.query.filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        return {"errors": ["Not found"]}, 404

    return note.to_dict(), 200


@app.patch("/notes/<int:note_id>")
def update_note(note_id):
    user = current_user()
    if not user:
        return {"errors": ["Unauthorized"]}, 401

    note = Note.query.filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        return {"errors": ["Not found"]}, 404

    data = request.get_json() or {}

    try:
        # Partial updates only modify provided fields
        if "title" in data:
            note.title = data["title"]
        if "body" in data:
            note.body = data["body"]
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return {"errors": [str(e)]}, 422

    return note.to_dict(), 200


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    user = current_user()
    if not user:
        return {"errors": ["Unauthorized"]}, 401

    note = Note.query.filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        return {"errors": ["Not found"]}, 404

    db.session.delete(note)
    db.session.commit()
    return {}, 200


if __name__ == "__main__":
    # Development-only entry point
    app.run(port=5555, debug=True)
