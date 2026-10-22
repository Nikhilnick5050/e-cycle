# E-Cycle — Smart E-Waste Management System

A full-stack web application for a college engineering project that helps users manage electronic waste through collection requests, smart segregation, reuse, repair, and responsible recycling.

**Tagline:** Recycle Today, Protect Tomorrow.

## Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript, Chart.js, Font Awesome
- **Backend:** Python + Flask
- **Database:** SQLite

## Features

- Responsive, mobile-first eco-friendly UI
- Home page with hero, feature cards, and circular-economy workflow
- Live dashboard with statistics and charts (calculated from real stored data)
- E-waste submission form with validation and unique request IDs
- Rule-based segregation and recommendation engine (not machine learning)
- Collection requests management: search, filter, sort, detail view, status update, delete, CSV export
- Segregation guide and About Project pages
- Basic admin login with hashed passwords and protected routes

## Setup & Run

1. Install Python 3.9+.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python app.py
   ```

4. Open http://127.0.0.1:5000 in your browser.

The SQLite database (`ecycle.db`) and its tables are created automatically on first launch.

## Default Admin Login

- **Username:** `admin`
- **Password:** `admin123`

Change this password after first login. In a real deployment, set the Flask `SECRET_KEY` from an environment variable.

## Project Structure

```
app.py              # Flask app: routes, API, auth, CSV export
database.py         # Database setup helpers (modular)
segregation.py      # Rule-based segregation engine (modular)
requirements.txt    # Python dependencies
templates/          # HTML templates (Jinja2)
static/style.css    # Global stylesheet
```

## Deployment

### Option A — Render (recommended, free)

Render gives Flask + SQLite a persistent disk, so your data survives restarts.

1. Push this project to a GitHub repository.
2. Go to [render.com](https://render.com) and sign in with GitHub.
3. Click **New > Blueprint**, connect your repo, and Render will read `render.yaml` automatically.
4. Render installs dependencies, starts the app with `gunicorn`, and gives you a public URL.
5. The SQLite database is stored on a 1 GB persistent disk (`/var/data/ecycle.db`).

### Option B — Railway or PythonAnywhere

Any host that supports Python/Flask works. Set the start command to `gunicorn app:app` (or `python app.py`), and set `SECRET_KEY` to a random value.

### Important note on SQLite

SQLite stores data in a local file. On hosts without a persistent disk (e.g. Vercel serverless functions), the database resets on every request and the dashboard will appear empty. Use a host with a persistent disk (Render, Railway, PythonAnywhere) or switch to a hosted database (e.g. PostgreSQL) for production.

## Limitations (honest notes)

- The segregation engine is **rule-based**, not machine learning.
- Recommendations are **preliminary**; final handling must follow local rules and authorised recycler guidance.
- Admin authentication is a basic prototype (single admin account, session-based).
- No real recycler partnerships, certifications, or statistics are claimed.