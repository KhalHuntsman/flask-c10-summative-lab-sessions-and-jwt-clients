#!/usr/bin/env python3
"""
Author: Hunter
Date: 2026-01-03
Version: 1.0
"""

from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

from config import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)

    # Stored hash is intentionally private and never directly exposed
    _password_hash = db.Column("password_hash", db.String, nullable=False)

    @validates("username")
    def validate_username(self, key, value):
        # Enforce presence and normalize whitespace at the model layer
        if not value or not value.strip():
            raise ValueError("Username is required.")
        return value.strip()

    @hybrid_property
    def password_hash(self):
        # Prevent exposing hashes through accidental reads or serialization
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password: str):
        # Centralizes password validation and hashing logic
        if not password or not password.strip():
            raise ValueError("Password is required.")
        pw_hash = bcrypt.generate_password_hash(password.strip()).decode("utf-8")
        self._password_hash = pw_hash

    def authenticate(self, password: str) -> bool:
        # Fail fast on empty input to avoid unnecessary hash checks
        if not password:
            return False
        return bcrypt.check_password_hash(self._password_hash, password)

    def to_dict(self):
        # Explicit serialization prevents leaking sensitive fields
        return {"id": self.id, "username": self.username}


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String, nullable=False)
    body = db.Column(db.Text, nullable=False)

    # Timestamps are handled automatically and always present
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Ownership is enforced at the database level
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship(
        "User",
        backref=db.backref("notes", cascade="all, delete-orphan")
    )

    def to_dict(self):
        # ISO formatting keeps timestamps JSON-safe and frontend-friendly
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id,
        }

    @validates("title", "body")
    def validate_text(self, key, value):
        # Shared validation logic ensures required text fields are non-empty
        if not value or not str(value).strip():
            raise ValueError(f"{key.capitalize()} is required.")
        return value.strip()
