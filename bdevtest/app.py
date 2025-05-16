# app.py - Main application file
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "rdkb_test_tracker_secret_key"
app.config['DATABASE'] = 'rdkb_test_tracker.db'

# Database initialization
def init_db():
    with sqlite3.connect(app.config['DATABASE']) as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            expected_result TEXT,
            status TEXT DEFAULT 'Not Started',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (feature_id) REFERENCES features (id)
        )
        ''')
        
        # Pre-populate features from the document
        features = [
            ('USP/TR-369', 'TR-369 User Services Platform functionality'),
            ('TR-069', 'TR-069 CPE WAN Management Protocol'),
            ('WebPA', 'Web Protocol for Applications'),
            ('WebConfig', 'Web Configuration Management'),
            ('SNMP', 'Simple Network Management Protocol'),
            ('Firmware upgrade', 'Firmware upgrade through xconf'),
            ('Telemetry 2.0', 'Telemetry data collection and reporting'),
            ('RFC', 'Remote Feature Control'),
            ('Local WebUI', 'Local Web User Interface'),
            ('SSH', 'Secure Shell access'),
            ('DAC', 'Device Application Container'),
            ('WAN connectivity', 'Wide Area Network connectivity'),
            ('LAN clients', 'Local Area Network client connectivity'),
            ('Wi-Fi', 'Wireless connectivity'),
            ('Factory reset', 'Factory reset functionality'),
            ('Bridge mode', 'Bridge mode functionality'),
            ('Self heal', 'Self healing functionality'),
            ('Parental control', 'Parental control functionality'),
            ('Firewall', 'Firewall functionality'),
            ('Backup and restore', 'Backup and restore functionality'),
            ('Log rotation', 'Log rotation functionality'),
            ('Log upload', 'Log upload functionality'),
        ]
        
        cursor = conn.cursor()
        for feature in features:
            # Check if feature already exists
            cursor.execute("SELECT id FROM features WHERE name = ?", (feature[0],))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO features (name, description) VALUES (?, ?)", feature)
        
        conn.commit()

# Routes
@app.route('/')
def index():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM features ORDER BY name")
    features = cursor.fetchall()
    conn.close()
    return render_template('index.html', features=features)

@app.route('/feature/<int:feature_id>')
def feature_details(feature_id):
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get feature details
    cursor.execute("SELECT * FROM features WHERE id = ?", (feature_id,))
    feature = cursor.fetchone()
    
    # Get test cases for this feature
    cursor.execute("SELECT * FROM test_cases WHERE feature_id = ? ORDER BY name", (feature_id,))
    test_cases = cursor.fetchall()
    
    conn.close()
    return render_template('feature.html', feature=feature, test_cases=test_cases)

@app.route('/add_test_case/<int:feature_id>', methods=['GET', 'POST'])
def add_test_case(feature_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        expected_result = request.form['expected_result']
        status = request.form['status']
        
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO test_cases (feature_id, name, description, expected_result, status) VALUES (?, ?, ?, ?, ?)",
            (feature_id, name, description, expected_result, status)
        )
        conn.commit()
        conn.close()
        
        flash('Test case added successfully!', 'success')
        return redirect(url_for('feature_details', feature_id=feature_id))
    
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM features WHERE id = ?", (feature_id,))
    feature = cursor.fetchone()
    conn.close()
    
    return render_template('add_test_case.html', feature=feature)

@app.route('/edit_test_case/<int:test_id>', methods=['GET', 'POST'])
def edit_test_case(test_id):
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        expected_result = request.form['expected_result']
        status = request.form['status']
        
        cursor.execute(
            "UPDATE test_cases SET name = ?, description = ?, expected_result = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name, description, expected_result, status, test_id)
        )
        conn.commit()
        
        # Get feature_id to redirect back to feature page
        cursor.execute("SELECT feature_id FROM test_cases WHERE id = ?", (test_id,))
        feature_id = cursor.fetchone()['feature_id']
        
        conn.close()
        flash('Test case updated successfully!', 'success')
        return redirect(url_for('feature_details', feature_id=feature_id))
    
    # Get test case details for editing
    cursor.execute("SELECT * FROM test_cases WHERE id = ?", (test_id,))
    test_case = cursor.fetchone()
    
    # Get feature details
    cursor.execute("SELECT * FROM features WHERE id = ?", (test_case['feature_id'],))
    feature = cursor.fetchone()
    
    conn.close()
    return render_template('edit_test_case.html', test_case=test_case, feature=feature)

@app.route('/delete_test_case/<int:test_id>', methods=['POST'])
def delete_test_case(test_id):
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Get feature_id before deleting
    cursor.execute("SELECT feature_id FROM test_cases WHERE id = ?", (test_id,))
    feature_id = cursor.fetchone()[0]
    
    # Delete the test case
    cursor.execute("DELETE FROM test_cases WHERE id = ?", (test_id,))
    conn.commit()
    conn.close()
    
    flash('Test case deleted successfully!', 'success')
    return redirect(url_for('feature_details', feature_id=feature_id))

# Run the application
if __name__ == '__main__':
    init_db()
    app.run(host='192.168.64.2', port=4555, debug=True)
