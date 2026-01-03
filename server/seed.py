#!/usr/bin/env python3
"""
Author: Hunter
Date: 2026-01-03
Version: 1.0
"""

from config import create_app, db
from models import User, Note

# App factory is required to safely access config and extensions
app = create_app()


def run_seed():
    with app.app_context():
        # Clear existing data in FK-safe order
        Note.query.delete()
        User.query.delete()
        db.session.commit()

        # Seed users with model-level password hashing
        hunter = User(username="hunter")
        hunter.password_hash = "password"

        flatiron = User(username="flatiron")
        flatiron.password_hash = "password"

        db.session.add_all([hunter, flatiron])
        db.session.commit()

        # Sample notes demonstrate ownership and pagination behavior
        notes = [
            Note(title="Welcome", body="This is your first note.", user_id=hunter.id),
            Note(
                title="Pagination",
                body="Try /notes?page=1&per_page=5 after logging in.",
                user_id=hunter.id,
            ),
            Note(
                title="Flatiron Note",
                body="Session auth is working and notes are protected.",
                user_id=flatiron.id,
            ),
        ]

        db.session.add_all(notes)
        db.session.commit()

        print("✅ Seed complete: users + notes created.")


if __name__ == "__main__":
    run_seed()
