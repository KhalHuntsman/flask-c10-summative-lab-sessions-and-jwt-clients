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

    # Core config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    # Database
    # For local dev, a sqlite file is fine. For deployment, DATABASE_URL should exist.
    default_db = "sqlite:///app.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", default_db)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Sessions
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Enable CORS for session cookies (credentials)
    CORS(app, supports_credentials=True)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    return app
