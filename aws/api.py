from flask import Flask, request, jsonify
import sqlite3
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import timedelta

# Configuración de la app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_production_jwt_secret_key'  # Cambia esto a un valor seguro
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "*"}})  # Habilitar CORS para solicitudes externas

# Registro de depuración de encabezados en cada solicitud
@app.before_request
def log_request_headers():
    print(f"[DEBUG] Encabezados recibidos: {request.headers}")

# Endpoint para registrar usuarios
@app.route('/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario"""
    try:
        data = request.json
        if not data or 'username' not in data or 'password' not in data or 'email' not in data:
            return jsonify({"message": "Faltan campos obligatorios"}), 400

        # Hash de la contraseña
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        # Insertar usuario en la base de datos
        conn = sqlite3.connect('nueva_base.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                       (data['username'], hashed_password, data['email'], 'User'))
        conn.commit()
        conn.close()

        print(f"[DEBUG] Usuario registrado: {data['username']}")
        return jsonify({"message": "Usuario registrado exitosamente"}), 201
    except sqlite3.IntegrityError as e:
        print(f"[ERROR] Usuario duplicado: {e}")
        return jsonify({"message": "El usuario o correo ya está registrado"}), 400
    except Exception as e:
        print(f"[ERROR] Error interno en registro: {e}")
        return jsonify({"message": "Error interno del servidor", "error": str(e)}), 500

# Endpoint para iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    """Autenticar un usuario y devolver un token JWT"""
    try:
        data = request.json
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"message": "Faltan campos obligatorios"}), 400

        # Consultar el usuario en la base de datos
        conn = sqlite3.connect('nueva_base.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, role FROM users WHERE username = ?", (data['username'],))
        user = cursor.fetchone()
        conn.close()

        if not user:
            print(f"[WARNING] Usuario no encontrado: {data['username']}")
            return jsonify({"message": "Credenciales inválidas"}), 401

        # Verificar la contraseña
        if bcrypt.check_password_hash(user['password'], data['password']):
            identity = f"{user['id']}|{user['role']}"
            token = create_access_token(identity=identity)
            print(f"[DEBUG] Usuario autenticado: {data['username']}, Token: {token}")
            return jsonify({"access_token": token}), 200
        else:
            print(f"[WARNING] Contraseña incorrecta para usuario: {data['username']}")
            return jsonify({"message": "Credenciales inválidas"}), 401

    except Exception as e:
        print(f"[ERROR] Error interno en login: {e}")
        return jsonify({"message": "Error interno del servidor", "error": str(e)}), 500

# Endpoint para obtener dispositivos
@app.route('/devices', methods=['GET'])
@jwt_required()
def get_devices():
    """Obtener dispositivos del usuario autenticado"""
    try:
        current_identity = get_jwt_identity()
        print(f"[DEBUG] Usuario autenticado: {current_identity}")
        user_id, user_role = current_identity.split('|')  # Descomponer "id|role"

        conn = sqlite3.connect('nueva_base.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT device_id, device_name, status FROM devices WHERE user_id = ?", (user_id,))
        devices = cursor.fetchall()
        conn.close()

        return jsonify([{
            "device_id": device['device_id'],
            "device_name": device['device_name'],
            "status": device['status']
        } for device in devices]), 200
    except Exception as e:
        print(f"[ERROR] Error al obtener dispositivos: {e}")
        return jsonify({"message": "Error al obtener dispositivos", "error": str(e)}), 500

# Endpoint para añadir un dispositivo
@app.route('/devices/add', methods=['POST'])
@jwt_required()
def add_device():
    """Agregar un dispositivo para el usuario autenticado"""
    try:
        current_identity = get_jwt_identity()
        user_id, user_role = current_identity.split('|')

        data = request.json
        if not data or 'device_name' not in data:
            return jsonify({"message": "Faltan campos obligatorios"}), 400

        # Insertar dispositivo en la base de datos
        conn = sqlite3.connect('nueva_base.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO devices (user_id, device_name, device_type, status) VALUES (?, ?, ?, ?)",
                       (user_id, data['device_name'], data.get('device_type', 'unknown'), data.get('status', 'activo')))
        conn.commit()
        conn.close()

        print(f"[DEBUG] Dispositivo añadido: {data['device_name']} para usuario {user_id}")
        return jsonify({"message": "Dispositivo añadido exitosamente"}), 201
    except Exception as e:
        print(f"[ERROR] Error al añadir dispositivo: {e}")
        return jsonify({"message": "Error al añadir dispositivo", "error": str(e)}), 500

# Ejecutar el servidor
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
