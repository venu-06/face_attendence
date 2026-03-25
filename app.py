# app.py

from flask import Flask, render_template, request, redirect, session
from utils.db import get_db
from utils.hash import hash_password, verify_password
from face_module.capture_faces import capture_faces
from face_module.train_lbph import train_model
from face_module.recognize_face import mark_attendance
import config
import sqlite3
import os

# Initialize Flask
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# ---------------------------
# LOGIN ROUTE
# ---------------------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, password FROM students WHERE email=?", (request.form["email"],))
        user = cur.fetchone()
        db.close()

        if user and verify_password(user[1], request.form["password"]):
            session["user"] = user[0]
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

# ---------------------------
# DASHBOARD ROUTE
# ---------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# ---------------------------
# REGISTER ROUTE
# ---------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required!")

        conn = get_db()
        cur = conn.cursor()

        # Check for duplicate email
        cur.execute("SELECT id FROM students WHERE email=?", (email,))
        if cur.fetchone():
            conn.close()
            return render_template("register.html", error="Email already registered!")

        # Insert student
        hashed_pw = hash_password(password)
        cur.execute(
            "INSERT INTO students (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_pw)
        )
        conn.commit()
        student_id = cur.lastrowid
        conn.close()

        # 🔥 Capture new student's face
        capture_faces(student_id)

        # 🔥 Re-train model with all students
        train_model()

        return redirect("/")

    return render_template("register.html")

# ---------------------------
# MARK ATTENDANCE ROUTE
# ---------------------------
@app.route("/mark")
def mark():
    if "user" not in session:
        return redirect("/")
    
    success = mark_attendance(session["user"])
    return "Attendance Marked ✅" if success else "Face Not Matched ❌"

# ---------------------------
# VIEW ATTENDANCE ROUTE
# ---------------------------
@app.route("/view")
def view():
    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    # Ensure session user is integer
    student_id = int(session["user"])

    cur.execute("""
        SELECT s.name, a.date, a.time, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.student_id = ?
        ORDER BY a.date, a.time
    """, (student_id,))

    records = cur.fetchall()
    db.close()

    # Debug: print records to check
    print(records)

    return render_template("view_attendance.html", records=records or [])

# ---------------------------
# LOGOUT ROUTE
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------------------
# RUN FLASK APP
# ---------------------------
if __name__ == "__main__":
    # Debug True + use_reloader=False avoids database locking issues
    app.run(debug=True, use_reloader=False)
