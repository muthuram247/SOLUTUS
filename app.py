from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "solutus.db"


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            mode TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'Submitted',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def categorize(text):
    text = text.lower()

    if any(word in text for word in ["food", "mess", "canteen", "hygiene"]):
        return "Food & Hygiene"
    if any(word in text for word in ["hostel", "room", "warden", "water"]):
        return "Hostel"
    if any(word in text for word in ["faculty", "teacher", "class", "lecture"]):
        return "Academic / Faculty"
    if any(word in text for word in ["road", "building", "fan", "light", "electricity"]):
        return "Infrastructure"
    if any(word in text for word in ["outpass", "leave", "permission"]):
        return "Outpass"
    if any(word in text for word in ["security", "harassment", "threat", "unsafe"]):
        return "Safety"

    return "General"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    mode = data.get("mode", "Anonymous")
    location = data.get("location", "").strip()

    if not title or not description:
        return jsonify({
            "success": False,
            "message": "Please enter the title and description."
        }), 400

    category = categorize(title + " " + description)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO complaints
        (title, description, category, mode, location, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        description,
        category,
        mode,
        location,
        "Submitted",
        created_at
    ))

    complaint_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "id": complaint_id,
        "category": category,
        "message": "Your issue has been submitted successfully."
    })


@app.route("/complaints")
def complaints():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT * FROM complaints
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/update/<int:complaint_id>", methods=["POST"])
def update_status(complaint_id):
    data = request.get_json()
    status = data.get("status")

    allowed = [
        "Submitted",
        "Under Review",
        "In Progress",
        "Resolved"
    ]

    if status not in allowed:
        return jsonify({
            "success": False,
            "message": "Invalid status."
        }), 400

    conn = sqlite3.connect(DB)

    conn.execute(
        "UPDATE complaints SET status = ? WHERE id = ?",
        (status, complaint_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Status updated."
    })


init_db()

if __name__ == "__main__":
    app.run(debug=True)