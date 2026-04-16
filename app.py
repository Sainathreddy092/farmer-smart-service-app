from flask import Flask, render_template, request, url_for
import sqlite3
import os
import math

app = Flask(__name__)

# upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# create database
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        skill TEXT,
        village TEXT,
        lat REAL,
        lon REAL,
        image TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# distance function
def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

# home page
@app.route('/')
def home():
    return render_template('index.html')

# add worker
@app.route('/add_worker', methods=['GET', 'POST'])
def add_worker():
    if request.method == 'POST':
        name = request.form['name']
        skill = request.form['skill']
        village = request.form['village']
        lat = float(request.form['lat'])
        lon = float(request.form['lon'])

        file = request.files['image']
        filename = file.filename

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO workers (name, skill, village, lat, lon, image) VALUES (?, ?, ?, ?, ?, ?)",
            (name, skill, village, lat, lon, filename)
        )

        conn.commit()
        conn.close()

        return "Worker Added Successfully!"

    return render_template('add_worker.html')

# find worker
@app.route('/find_worker', methods=['GET', 'POST'])
def find_worker():
    if request.method == 'POST':
        skill = request.form['skill']
        job_lat = float(request.form['lat'])
        job_lon = float(request.form['lon'])

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT name, skill, village, lat, lon, image FROM workers WHERE skill=?", (skill,))
        data = cur.fetchall()

        conn.close()

        results = []

        for w in data:
            dist = calculate_distance(job_lat, job_lon, w[3], w[4])

            if dist < 50:
                results.append({
                    "name": w[0],
                    "skill": w[1],
                    "village": w[2],
                    "image": w[5]
                })

        return render_template('find_worker.html', results=results)

    return render_template('find_worker.html', results=None)

# run app
if __name__ == "__main__":
    app.run(debug=True)