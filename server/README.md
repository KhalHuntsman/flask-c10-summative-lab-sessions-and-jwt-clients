# Flask Notes API (Session-Based Authentication)

## Overview

This project is a **Flask-based REST API** that implements **secure session-based authentication** and a **user-owned Notes resource**.

The backend is designed to integrate with a provided React frontend that handles user login, signup, and session persistence. Authenticated users can create, view, update, and delete their own notes, while access to other users’ data is strictly prevented.

The API also implements pagination on the notes index route to ensure scalability and performance.

---

### Features

- Session-based authentication
- Secure password hashing with bcrypt
- Protected routes requiring authentication
- User-owned Notes resource
- Full CRUD operations for notes
- Paginated index route for notes
- Database migrations using Flask-Migrate
- Seed file for local development
- Clean and maintainable project structure

---

### Authentication Endpoints

#### POST `/signup`

Creates a new user account and starts a session.

**Request Body**
```json
{
  "username": "string",
  "password": "string",
  "password_confirmation": "string"
}

#### Response

{
  "id": 1,
  "username": "string"
}

#### POST /login
- Authenticates an existing user and starts a session.

#### Request Body
{
  "username": "string",
  "password": "string"
}

#### GET /check_session
- Checks if a user session is active.
- Returns user data if logged in
- Returns {} with status 401 if not authenticated

#### DELETE /logout
- Ends the current user session.

#### Notes Resource (Protected)
- All /notes routes require an authenticated session.

#### GET /notes
- Returns paginated notes owned by the logged-in user.

### Query Parameters

- page (default: 1)
- per_page (default: 10)

#### Example Response
{
  "page": 1,
  "per_page": 5,
  "total": 12,
  "total_pages": 3,
  "items": [
    {
      "id": 1,
      "title": "Welcome",
      "body": "This is your first note.",
      "created_at": "2026-01-03T15:05:55",
      "updated_at": "2026-01-03T15:05:55",
      "user_id": 1
    }
  ]
}

#### POST /notes
- Creates a new note for the logged-in user.

#### GET /notes/<id>
- Returns a single note owned by the logged-in user.

#### PATCH /notes/<id>
- Updates a note owned by the logged-in user.

#### DELETE /notes/<id>
- Deletes a note owned by the logged-in user.

### Technologies Used
#### Backend
- Python 3

#### Flask
##### Flask Extensions
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- Flask-CORS

#### Database
- SQLite (development)
- PostgreSQL-compatible (production-ready)

#### Tooling
- Pipenv
- Git & GitHub

### File Structure
All paths are relative to the repository root.

- flask-c10-summative-lab-sessions-and-jwt-clients/server/app.py
- flask-c10-summative-lab-sessions-and-jwt-clients/server/config.py
- flask-c10-summative-lab-sessions-and-jwt-clients/server/models.py
- flask-c10-summative-lab-sessions-and-jwt-clients/server/seed.py
- flask-c10-summative-lab-sessions-and-jwt-clients/server/migrations/
- flask-c10-summative-lab-sessions-and-jwt-clients/server/instance/
- flask-c10-summative-lab-sessions-and-jwt-clients/server/Pipfile
- flask-c10-summative-lab-sessions-and-jwt-clients/server/Pipfile.lock
- flask-c10-summative-lab-sessions-and-jwt-clients/server/README.md

### Key Files Explained
#### server/app.py
- Defines all API routes
- Handles authentication and session management
- Implements CRUD operations for notes
- Enforces user ownership and authorization
- Implements pagination on the notes index route

#### server/models.py
- Defines User and Note SQLAlchemy models
- Implements password hashing and authentication logic
- Validates required fields

#### server/config.py
- Application factory
- Database, migrations, bcrypt, and CORS configuration
- Environment-safe setup for development and deployment

#### server/seed.py
- Populates the database with sample users and notes
- Safe to run multiple times during development

### Running the Project
#### Setup
- pipenv install
- pipenv shell
- cd server
#### Database Setup
- flask db upgrade
- python seed.py
#### Start the Server
- python app.py

#### The server runs on: 
- http://localhost:5555

### License
Educational use only.
Built for learning secure Flask API design, authentication, and pagination.

### ### Additional notes:
- Project passed through ChatGPT for syntax and grammatical error checking and for writing this README.md. Everything was double checked for accuracy and readability prior to submission.