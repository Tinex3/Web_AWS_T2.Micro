from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Habilita CORS para la API
DATABASE = 'database.db'

# Helper function to interact with the database
def execute_query(query, args=(), fetchone=False, fetchall=False, commit=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    if commit:
        conn.commit()
    conn.close()
    return result

# Initialize the database (if not already initialized)
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Create tables
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            role TEXT DEFAULT 'User'
        );

        CREATE TABLE IF NOT EXISTS roles (
            role_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            permissions TEXT
        );

        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(role_id) REFERENCES roles(role_id)
        );

        CREATE TABLE IF NOT EXISTS devices (
            device_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            device_name TEXT NOT NULL,
            device_type TEXT,
            status TEXT DEFAULT 'activo',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS device_parameters (
            parameter_id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            status TEXT DEFAULT 'activo',
            variable_1 REAL,
            variable_2 REAL,
            data_1 REAL,
            data_2 REAL,
            battery_voltage REAL,
            error_code TEXT,
            sampling_time REAL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(device_id) REFERENCES devices(device_id)
        );

        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS flask_sessions (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            expiry DATETIME NOT NULL
        );
        """)
        conn.commit()

# Endpoint to register a user
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        execute_query(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, password, email),
            commit=True
        )
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'User with this username or email already exists'}), 400

# Endpoint to login a user
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    user = execute_query(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
        fetchone=True
    )

    if user:
        session_id = f"session-{user['id']}-{datetime.now().timestamp()}"
        expires_at = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        execute_query(
            "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)",
            (session_id, user['id'], expires_at),
            commit=True
        )
        return jsonify({'message': 'Login successful', 'session_id': session_id}), 200

    return jsonify({'error': 'Invalid username or password'}), 401

# Endpoint to add a device
@app.route('/devices', methods=['POST'])
def add_device():
    data = request.json
    user_id = data.get('user_id')
    device_name = data.get('device_name')
    device_type = data.get('device_type')

    if not user_id or not device_name:
        return jsonify({'error': 'Missing required fields'}), 400

    execute_query(
        "INSERT INTO devices (user_id, device_name, device_type) VALUES (?, ?, ?)",
        (user_id, device_name, device_type),
        commit=True
    )
    return jsonify({'message': 'Device added successfully'}), 201

# Endpoint to get all devices
@app.route('/devices', methods=['GET'])
def get_devices():
    devices = execute_query("SELECT * FROM devices", fetchall=True)
    return jsonify([dict(device) for device in devices]), 200

# Endpoint to add sensor data
@app.route('/device_parameters', methods=['POST'])
def add_device_parameters():
    data = request.json
    device_id = data.get('device_id')
    variable_1 = data.get('variable_1')
    variable_2 = data.get('variable_2')
    data_1 = data.get('data_1')
    data_2 = data.get('data_2')
    battery_voltage = data.get('battery_voltage')
    error_code = data.get('error_code')
    sampling_time = data.get('sampling_time')

    if not device_id:
        return jsonify({'error': 'Device ID is required'}), 400

    execute_query(
        """
        INSERT INTO device_parameters (
            device_id, variable_1, variable_2, data_1, data_2, battery_voltage, error_code, sampling_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (device_id, variable_1, variable_2, data_1, data_2, battery_voltage, error_code, sampling_time),
        commit=True
    )
    return jsonify({'message': 'Device parameters added successfully'}), 201

# Endpoint to get device parameters
@app.route('/device_parameters/<int:device_id>', methods=['GET'])
def get_device_parameters(device_id):
    parameters = execute_query(
        "SELECT * FROM device_parameters WHERE device_id = ?",
        (device_id,),
        fetchall=True
    )
    return jsonify([dict(param) for param in parameters]), 200


#temp
@app.route('/users', methods=['GET'])
def get_users():
    users = execute_query("SELECT id, username, email, created_at FROM users", fetchall=True)
    return jsonify([dict(user) for user in users]), 200
if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(host='0.0.0.0', port=5000, debug=True)
