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

# Extension instances are created once and bound to the app in the factory
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


def create_app(env_name: str = "dev") -> Flask:
    # Application factory allows clean separation of config and runtime
    app = Flask(__name__)

    # Secret key pulled from environment with a safe dev fallback
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    # Resolve absolute paths to avoid cwd-related issues
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

    # Instance folder is used for runtime data (e.g., sqlite db)
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    # Default to a local sqlite database if no DATABASE_URL is provided
    default_db = f"sqlite:///{os.path.join(INSTANCE_DIR, 'app.db')}"
    db_url = os.getenv("DATABASE_URL", default_db)

    # Normalize legacy Heroku postgres URLs for SQLAlchemy compatibility
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Basic session hardening for cookie-based auth
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Required for frontend apps using session-based authentication
    CORS(app, supports_credentials=True)

    # Bind extensions to the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    return app
