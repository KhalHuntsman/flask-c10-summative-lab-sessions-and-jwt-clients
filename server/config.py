#!/usr/bin/env python3
"""
Author: Hunter
Date: 2026-01-03
Version: 1.0
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


def create_app(env_name: str = "dev") -> Flask:
    app = Flask(__name__)

    # ------------------------------------------------------------------
    # Core Config
    # ------------------------------------------------------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    # ------------------------------------------------------------------
    # Instance Folder (absolute path, always safe)
    # ------------------------------------------------------------------
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

    os.makedirs(INSTANCE_DIR, exist_ok=True)

    # ------------------------------------------------------------------
    # Database Config
    # ------------------------------------------------------------------
    default_db = f"sqlite:///{os.path.join(INSTANCE_DIR, 'app.db')}"
    db_url = os.getenv("DATABASE_URL", default_db)

    # Fix Heroku-style postgres URLs if present
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ------------------------------------------------------------------
    # Session Security
    # ------------------------------------------------------------------
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Enable credentials for session-based auth
    CORS(app, supports_credentials=True)

    # ------------------------------------------------------------------
    # Init Extensions
    # ------------------------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    return app
