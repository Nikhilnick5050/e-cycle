"""
E-Cycle — Smart E-Waste Management System
=========================================
A full-stack web application for a college engineering project.

Stack: Flask (Python) + SQLite + HTML/CSS/JS + Chart.js + Font Awesome.

Run locally:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""

import csv
import io
import os
import sqlite3
import uuid
from datetime import datetime
from functools import wraps

from flask import (Flask, Response, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# On Render, DB_PATH points to the persistent disk (see render.yaml).
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "ecycle.db"))

app = Flask(__name__)
# NOTE: In a real deployment, set this from an environment variable.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ecycle-dev-secret-change-me")

# ---------------------------------------------------------------------------
# Database helpers (parameterized queries only)
# ---------------------------------------------------------------------------
def get_db():
    """Open a connection to SQLite for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables automatically on first launch."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS e_waste_requests (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id     TEXT UNIQUE NOT NULL,
            submitted_at   TEXT NOT NULL,
            full_name      TEXT NOT NULL,
            contact        TEXT NOT NULL,
            pickup_location TEXT NOT NULL,
            item_type      TEXT NOT NULL,
            condition      TEXT NOT NULL,
            quantity       INTEGER NOT NULL,
            notes          TEXT,
            category       TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            status         TEXT NOT NULL DEFAULT 'Pending'
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )

    # Create a default admin account on first launch (change the password!).
    cur.execute("SELECT COUNT(*) FROM admins")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123")),
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Segregation / recommendation engine (rule-based, not machine learning)
# ---------------------------------------------------------------------------
ITEM_TYPES = [
    "Mobile Phone",
    "Laptop",
    "Battery",
    "Charger / Cable",
    "Tablet",
    "Television / Monitor",
    "Computer / Desktop",
    "Printer",
    "Other Electronic Item",
]

CONDITIONS = ["Working", "Repairable", "Damaged / Not Working"]

STATUSES = ["Pending", "Collected", "Completed"]


def classify_item(item_type, condition):
    """
    Rule-based classification.

    Returns (category, recommendation). The recommendation is preliminary;
    final handling must follow local rules and authorized recycler guidance.
    """
    item_type = (item_type or "").strip()
    condition = (condition or "").strip()

    # Rule 4: batteries always get special handling.
    if item_type == "Battery":
        return (
            "Special Handling",
            "Batteries must always be handled separately. Never open, crush, "
            "burn, or throw them in ordinary household waste. Take them to an "
            "authorized battery collection point.",
        )

    # Rule 5: chargers and cables.
    if item_type == "Charger / Cable":
        return (
            "Recyclable",
            "Collect for responsible recovery of electronic materials "
            "(copper, plastic, etc.) at an authorized e-waste facility.",
        )

    # Rule 6: TVs and monitors need careful handling.
    if item_type == "Television / Monitor":
        return (
            "Recyclable",
            "Handle carefully (glass and hazardous materials). Deliver to an "
            "authorized e-waste collection facility; never break or burn it.",
        )

    # Rules 1-3: condition-based for general devices.
    if condition == "Working":
        return (
            "Reusable",
            "Recommend reuse, donation, or refurbishment. If the item is no "
            "longer needed, direct it to an authorized collection point.",
        )
    if condition == "Repairable":
        return (
            "Repairable",
            "Recommend professional repair first to extend product life. If "
            "repair is impractical, direct it to authorized recycling.",
        )
    if condition == "Damaged / Not Working":
        return (
            "Recyclable",
            "Handle safely and deliver to an authorized e-waste collection "
            "facility for responsible recycling.",
        )

    return ("Recyclable", "Deliver to an authorized e-waste collection facility.")


def generate_request_id():
    """Generate a unique, human-readable request ID."""
    stamp = datetime.now().strftime("%Y%m%d")
    return f"EC-{stamp}-{uuid.uuid4().hex[:6].upper()}"


# ---------------------------------------------------------------------------
# Admin authentication helpers
# ---------------------------------------------------------------------------
def admin_required(view):
    """Protect a route so only logged-in administrators can access it."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        # Read and validate inputs.
        full_name = (request.form.get("full_name") or "").strip()
        contact = (request.form.get("contact") or "").strip()
        pickup_location = (request.form.get("pickup_location") or "").strip()
        item_type = (request.form.get("item_type") or "").strip()
        condition = (request.form.get("condition") or "").strip()
        notes = (request.form.get("notes") or "").strip()

        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not contact:
            errors.append("Contact number or email is required.")
        if not pickup_location:
            errors.append("Pickup location is required.")
        if item_type not in ITEM_TYPES:
            errors.append("Please choose a valid electronic item type.")
        if condition not in CONDITIONS:
            errors.append("Please choose a valid item condition.")

        # Quantity: must be a whole number >= 1.
        try:
            quantity = int(request.form.get("quantity", "0"))
        except ValueError:
            quantity = 0
        if quantity < 1:
            errors.append("Quantity must be at least 1.")

        if errors:
            return render_template(
                "submit.html",
                errors=errors,
                form=request.form,
                item_types=ITEM_TYPES,
                conditions=CONDITIONS,
            )

        category, recommendation = classify_item(item_type, condition)
        request_id = generate_request_id()
        submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db = get_db()
        db.execute(
            """
            INSERT INTO e_waste_requests
                (request_id, submitted_at, full_name, contact, pickup_location,
                 item_type, condition, quantity, notes, category,
                 recommendation, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id, submitted_at, full_name, contact, pickup_location,
                item_type, condition, quantity, notes, category,
                recommendation, "Pending",
            ),
        )
        db.commit()

        return render_template(
            "submit.html",
            success=True,
            request_id=request_id,
            category=category,
            recommendation=recommendation,
            item_types=ITEM_TYPES,
            conditions=CONDITIONS,
        )

    return render_template(
        "submit.html", item_types=ITEM_TYPES, conditions=CONDITIONS, form={}
    )


@app.route("/requests")
def requests_page():
    return render_template(
        "requests.html", item_types=ITEM_TYPES, conditions=CONDITIONS,
        statuses=STATUSES,
    )


@app.route("/guide")
def guide():
    return render_template("guide.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ---------------------------------------------------------------------------
# JSON API (used by the dashboard and requests pages)
# ---------------------------------------------------------------------------
@app.route("/api/stats")
def api_stats():
    db = get_db()

    total_requests = db.execute(
        "SELECT COUNT(*) AS c FROM e_waste_requests"
    ).fetchone()["c"]

    total_items = db.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS s FROM e_waste_requests"
    ).fetchone()["s"]

    pending = db.execute(
        "SELECT COUNT(*) AS c FROM e_waste_requests WHERE status = 'Pending'"
    ).fetchone()["c"]
    collected = db.execute(
        "SELECT COUNT(*) AS c FROM e_waste_requests WHERE status = 'Collected'"
    ).fetchone()["c"]
    completed = db.execute(
        "SELECT COUNT(*) AS c FROM e_waste_requests WHERE status = 'Completed'"
    ).fetchone()["c"]

    reusable = db.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS s FROM e_waste_requests "
        "WHERE category = 'Reusable'"
    ).fetchone()["s"]
    repairable = db.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS s FROM e_waste_requests "
        "WHERE category = 'Repairable'"
    ).fetchone()["s"]
    recyclable = db.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS s FROM e_waste_requests "
        "WHERE category = 'Recyclable'"
    ).fetchone()["s"]
    special = db.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS s FROM e_waste_requests "
        "WHERE category = 'Special Handling'"
    ).fetchone()["s"]

    # Requests grouped by item type (for the bar chart).
    by_type_rows = db.execute(
        "SELECT item_type, COUNT(*) AS c FROM e_waste_requests "
        "GROUP BY item_type ORDER BY c DESC"
    ).fetchall()
    by_type = {r["item_type"]: r["c"] for r in by_type_rows}

    # Requests grouped by condition (for the doughnut chart).
    by_condition_rows = db.execute(
        "SELECT condition, COUNT(*) AS c FROM e_waste_requests "
        "GROUP BY condition"
    ).fetchall()
    by_condition = {r["condition"]: r["c"] for r in by_condition_rows}

    recent = db.execute(
        "SELECT * FROM e_waste_requests ORDER BY submitted_at DESC, id DESC "
        "LIMIT 8"
    ).fetchall()

    return jsonify(
        {
            "total_requests": total_requests,
            "total_items": total_items,
            "pending": pending,
            "collected": collected,
            "completed": completed,
            "reusable": reusable,
            "repairable": repairable,
            "recyclable": recyclable,
            "special": special,
            "by_type": by_type,
            "by_condition": by_condition,
            "recent": [dict(r) for r in recent],
        }
    )


@app.route("/api/requests")
def api_requests():
    db = get_db()

    # Filters and search (all parameterized).
    q = (request.args.get("q") or "").strip()
    item_type = (request.args.get("item_type") or "").strip()
    condition = (request.args.get("condition") or "").strip()
    status = (request.args.get("status") or "").strip()
    sort = (request.args.get("sort") or "newest").strip()

    sql = "SELECT * FROM e_waste_requests WHERE 1=1"
    params = []

    if q:
        sql += " AND (request_id LIKE ? OR full_name LIKE ?)"
        like = f"%{q}%"
        params += [like, like]
    if item_type:
        sql += " AND item_type = ?"
        params.append(item_type)
    if condition:
        sql += " AND condition = ?"
        params.append(condition)
    if status:
        sql += " AND status = ?"
        params.append(status)

    if sort == "oldest":
        sql += " ORDER BY submitted_at ASC, id ASC"
    else:
        sql += " ORDER BY submitted_at DESC, id DESC"

    rows = db.execute(sql, params).fetchall()
    return jsonify({"requests": [dict(r) for r in rows]})


@app.route("/api/requests/<int:req_id>/status", methods=["POST"])
@admin_required
def api_update_status(req_id):
    db = get_db()
    new_status = (request.json or {}).get("status", "")
    if new_status not in STATUSES:
        return jsonify({"error": "Invalid status."}), 400
    db.execute(
        "UPDATE e_waste_requests SET status = ? WHERE id = ?",
        (new_status, req_id),
    )
    db.commit()
    return jsonify({"ok": True})


@app.route("/api/requests/<int:req_id>", methods=["DELETE"])
@admin_required
def api_delete_request(req_id):
    db = get_db()
    db.execute("DELETE FROM e_waste_requests WHERE id = ?", (req_id,))
    db.commit()
    return jsonify({"ok": True})


@app.route("/export.csv")
def export_csv():
    """Export the currently displayed requests as a CSV file."""
    db = get_db()

    q = (request.args.get("q") or "").strip()
    item_type = (request.args.get("item_type") or "").strip()
    condition = (request.args.get("condition") or "").strip()
    status = (request.args.get("status") or "").strip()

    sql = "SELECT * FROM e_waste_requests WHERE 1=1"
    params = []
    if q:
        sql += " AND (request_id LIKE ? OR full_name LIKE ?)"
        like = f"%{q}%"
        params += [like, like]
    if item_type:
        sql += " AND item_type = ?"
        params.append(item_type)
    if condition:
        sql += " AND condition = ?"
        params.append(condition)
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY submitted_at DESC, id DESC"

    rows = db.execute(sql, params).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Request ID", "Submission Date", "Name", "Contact",
            "Pickup Location", "Item Type", "Condition", "Quantity",
            "Recommended Action", "Status",
        ]
    )
    for r in rows:
        writer.writerow(
            [
                r["request_id"], r["submitted_at"], r["full_name"],
                r["contact"], r["pickup_location"], r["item_type"],
                r["condition"], r["quantity"], r["recommendation"],
                r["status"],
            ]
        )

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=ecycle_requests.csv"},
    )


# ---------------------------------------------------------------------------
# Admin login / logout
# ---------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        db = get_db()
        row = db.execute(
            "SELECT * FROM admins WHERE username = ?", (username,)
        ).fetchone()

        if row and check_password_hash(row["password_hash"], password):
            session["is_admin"] = True
            session["admin_user"] = username
            return redirect(url_for("requests_page"))
        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)