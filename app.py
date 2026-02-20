from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")
def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            role TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            status TEXT
        )
    """)
    db.commit()
    db.close()
init_db()
# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            return redirect(url_for("dashboard", role=user[0]))

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard/<role>")
def dashboard(role):
    return render_template("dashboard.html", user=role)

# ---------- UPLOAD ----------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))

            db = get_db()
            db.execute(
                "INSERT INTO files (filename, status) VALUES (?, ?)",
                (file.filename, "Pending")
            )
            db.commit()

            return redirect("/files")

    return render_template("upload.html")

# ---------- FILE LIST ----------
@app.route("/files")
def files():
    db = get_db()
    files = db.execute("SELECT * FROM files").fetchall()
    return render_template("files.html", files=files)

# ---------- APPROVE / REJECT ----------
@app.route("/approve/<int:file_id>", methods=["POST"])
def approve(file_id):
    db = get_db()
    db.execute("UPDATE files SET status='Approved' WHERE id=?", (file_id,))
    db.commit()
    return redirect("/files")

@app.route("/reject/<int:file_id>", methods=["POST"])
def reject(file_id):
    db = get_db()
    db.execute("UPDATE files SET status='Changes Requested' WHERE id=?", (file_id,))
    db.commit()
    return redirect("/files")

if __name__ == "__main__":
    app.run(debug=True)