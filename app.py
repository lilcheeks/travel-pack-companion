from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'data/packing.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Create tables for Trips and Items
with get_db() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY, name TEXT, date TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, trip_id INTEGER, name TEXT, category TEXT, packed INTEGER DEFAULT 0)')

@app.route('/')
def index():
    with get_db() as conn:
        trips = conn.execute('SELECT * FROM trips ORDER BY id DESC').fetchall()
    return render_template('index.html', trips=trips)

@app.route('/create_trip', methods=['POST'])
def create_trip():
    name = request.form.get('name')
    template = request.form.get('template') # e.g., "International" or "Cottage"
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO trips (name) VALUES (?)', (name,))
        trip_id = cur.lastrowid
        
        # Default Logic: Add basic items automatically based on your "Template" choice
        defaults = ['Passport', 'Phone Charger', 'Socks', 'Toothbrush']
        if template == 'Cottage':
            defaults += ['Swimsuit', 'Bug Spray', 'Water Filter']
            
        for item in defaults:
            conn.execute('INSERT INTO items (trip_id, name, packed) VALUES (?, ?, 0)', (trip_id, item))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
