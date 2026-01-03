#!/usr/bin/env python3
"""
Author: Hunter
Date: 2026-01-03
Version: 1.0
"""

from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from config import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)

    _password_hash = db.Column("password_hash", db.String, nullable=False)

    @validates("username")
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError("Username is required.")
        return value.strip()

    @hybrid_property
    def password_hash(self):
        # Prevent exposing hashes through accidental reads/serialization
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password: str):
        if not password or not password.strip():
            raise ValueError("Password is required.")
        pw_hash = bcrypt.generate_password_hash(password.strip()).decode("utf-8")
        self._password_hash = pw_hash

    def authenticate(self, password: str) -> bool:
        if not password:
            return False
        return bcrypt.check_password_hash(self._password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username}
