from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'data/packing.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Database Initialization with new columns
with get_db() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY, name TEXT, date DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('''CREATE TABLE IF NOT EXISTS items 
                 (id INTEGER PRIMARY KEY, trip_id INTEGER, name TEXT, 
                  category TEXT DEFAULT "General", quantity INTEGER DEFAULT 1, packed INTEGER DEFAULT 0)''')

@app.route('/')
def index():
    with get_db() as conn:
        trips = conn.execute('SELECT * FROM trips ORDER BY id DESC').fetchall()
    return render_template('index.html', trips=trips)

@app.route('/create_trip', methods=['POST'])
def create_trip():
    name = request.form.get('name')
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO trips (name) VALUES (?)', (name,))
    return redirect(url_for('index'))

@app.route('/trip/<int:trip_id>')
def view_trip(trip_id):
    with get_db() as conn:
        trip = conn.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()
        # Fetch items sorted by category
        items = conn.execute('SELECT * FROM items WHERE trip_id = ? ORDER BY category, name', (trip_id,)).fetchall()
    return render_template('trip.html', trip=trip, items=items)

@app.route('/add_item/<int:trip_id>', methods=['POST'])
def add_item(trip_id):
    name = request.form.get('name')
    cat = request.form.get('category', 'General')
    qty = request.form.get('quantity', 1)
    with get_db() as conn:
        conn.execute('INSERT INTO items (trip_id, name, category, quantity) VALUES (?, ?, ?, ?)', (trip_id, name, cat, qty))
    return redirect(url_for('view_trip', trip_id=trip_id))

@app.route('/delete_trip/<int:trip_id>', methods=['POST'])
def delete_trip(trip_id):
    with get_db() as conn:
        conn.execute('DELETE FROM items WHERE trip_id = ?', (trip_id,))
        conn.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    return redirect(url_for('index'))

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    with get_db() as conn:
        # Get the trip_id before deleting so we can redirect back to the right page
        item = conn.execute('SELECT trip_id FROM items WHERE id = ?', (item_id,)).fetchone()
        if item:
            trip_id = item['trip_id']
            conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
            return redirect(url_for('view_trip', trip_id=trip_id))
    return redirect(url_for('index'))

@app.route('/toggle/<int:item_id>', methods=['POST'])
def toggle_item(item_id):
    with get_db() as conn:
        conn.execute('UPDATE items SET packed = 1 - packed WHERE id = ?', (item_id,))
    return jsonify(success=True)

@app.route('/static/<path:filename>')
def serve_static(filename):
    # This tells Flask to look in the 'static' folder for the file
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
