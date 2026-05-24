from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "postgres-service"),
        database=os.environ.get("DB_NAME", "homeservices"),
        user=os.environ.get("DB_USER", "admin"),
        password=os.environ.get("DB_PASSWORD", "password")
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            service VARCHAR(100),
            date VARCHAR(50),
            phone VARCHAR(20),
            status VARCHAR(20) DEFAULT 'Pending'
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

@app.route("/bookings", methods=["GET", "POST"])
def bookings():
    if request.method == "POST":
        name = request.form["name"]
        service = request.form["service"]
        date = request.form["date"]
        phone = request.form["phone"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bookings (name, service, date, phone) VALUES (%s, %s, %s, %s)",
            (name, service, date, phone)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("bookings"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, service, date, phone, status FROM bookings ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("bookings.html", bookings=rows)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)