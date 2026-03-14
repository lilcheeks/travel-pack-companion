from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'data/packing.db'

# Ensure the data directory exists for your Docker volume
if not os.path.exists('data'):
    os.makedirs('data')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
with get_db() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY, name TEXT, date DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, trip_id INTEGER, name TEXT, category TEXT, packed INTEGER DEFAULT 0)')

@app.route('/')
def index():
    with get_db() as conn:
        trips = conn.execute('SELECT * FROM trips ORDER BY id DESC').fetchall()
    return render_template('index.html', trips=trips)

@app.route('/create_trip', methods=['POST'])
def create_trip():
    name = request.form.get('name')
    template = request.form.get('template')
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO trips (name) VALUES (?)', (name,))
        trip_id = cur.lastrowid
        
        # Default items - we can expand these later!
        defaults = ['Passport', 'Phone Charger', 'Socks', 'Toothbrush', 'Deodorant']
        if template == 'Cottage':
            defaults += ['Swimsuit', 'Bug Spray', 'Flashlight', 'Sunscreen']
            
        for item in defaults:
            conn.execute('INSERT INTO items (trip_id, name, packed) VALUES (?, ?, 0)', (trip_id, item))
    return redirect(url_for('index'))

@app.route('/trip/<int:trip_id>')
def view_trip(trip_id):
    with get_db() as conn:
        trip = conn.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()
        items = conn.execute('SELECT * FROM items WHERE trip_id = ?', (trip_id,)).fetchall()
    return render_template('trip.html', trip=trip, items=items)

@app.route('/toggle/<int:item_id>', methods=['POST'])
def toggle_item(item_id):
    with get_db() as conn:
        conn.execute('UPDATE items SET packed = 1 - packed WHERE id = ?', (item_id,))
    return jsonify(success=True)

@app.route('/clone_trip/<int:old_trip_id>', methods=['POST'])
def clone_trip(old_trip_id):
    new_name = request.form.get('new_name')
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO trips (name) VALUES (?)', (new_name,))
        new_trip_id = cur.lastrowid
        conn.execute('INSERT INTO items (trip_id, name, packed) SELECT ?, name, 0 FROM items WHERE trip_id = ?', (new_trip_id, old_trip_id))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
