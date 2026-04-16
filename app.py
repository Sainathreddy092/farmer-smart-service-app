import streamlit as st
import sqlite3
import os
import math

# ---------------- SETUP ----------------
st.set_page_config(page_title="Farmer Service App", layout="centered")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        skill TEXT,
        village TEXT,
        phone TEXT,
        lat REAL,
        lon REAL,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- DISTANCE ----------------
def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

# ---------------- UI ----------------
st.title("🌾 Farmer Service Platform")

menu = st.sidebar.radio("Menu", ["Add Worker", "Find Worker"])

# ---------------- ADD WORKER ----------------
if menu == "Add Worker":
    st.subheader("➕ Add Worker")

    name = st.text_input("Name")
    skill = st.selectbox("Skill", ["ploughing", "harvesting", "spraying", "repair"])
    village = st.text_input("Village")
    phone = st.text_input("Phone Number")
    lat = st.number_input("Latitude")
    lon = st.number_input("Longitude")
    image = st.file_uploader("Upload Image")

    if st.button("Save Worker"):
        if name and phone and image is not None:

            filepath = os.path.join(UPLOAD_FOLDER, image.name)

            with open(filepath, "wb") as f:
                f.write(image.read())

            conn = sqlite3.connect("database.db")
            cur = conn.cursor()

            cur.execute("""
            INSERT INTO workers (name, skill, village, phone, lat, lon, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, skill, village, phone, lat, lon, image.name))

            conn.commit()
            conn.close()

            st.success("Worker Added Successfully ✅")

        else:
            st.error("Please fill all fields")

# ---------------- FIND WORKER ----------------
if menu == "Find Worker":
    st.subheader("🔍 Find Nearby Workers")

    skill = st.selectbox("Skill Required", ["ploughing", "harvesting", "spraying", "repair"])
    lat = st.number_input("Your Latitude")
    lon = st.number_input("Your Longitude")

    if st.button("Search Workers"):
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("""
        SELECT name, skill, village, phone, lat, lon, image
        FROM workers
        WHERE skill=?
        """, (skill,))

        data = cur.fetchall()
        conn.close()

        results = []

        for w in data:
            dist = distance(lat, lon, w[4], w[5])

            if dist < 50:
                results.append(w)

        if results:
            st.success(f"{len(results)} Workers Found")

            for w in results:
                st.image(os.path.join("uploads", w[6]), width=150)
                st.write("👤 Name:", w[0])
                st.write("🌾 Skill:", w[1])
                st.write("🏡 Village:", w[2])
                st.write("📞 Phone:", w[3])
                st.write("📍 Distance:", round(distance(lat, lon, w[4], w[5]), 2))
                st.markdown("---")

        else:
            st.warning("No workers found nearby")
