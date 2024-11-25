from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Ruta para manejar dispositivos
@app.route('/devices', methods=['GET'])
def devices():
    conn = None  # Inicializamos conn con None para evitar problemas
    try:
        # Obtener el user_id de las cookies
        user_id = request.cookies.get('user_id')
        if not user_id:
            return jsonify({"message": "No autorizado"}), 401

        # Conectar a la base de datos SQLite
        conn = sqlite3.connect('nueva_base.db')
        cursor = conn.cursor()

        # Verificar si el usuario existe
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "No autorizado"}), 401

        # Simulación de dispositivos
        devices = [
            {"id": 1, "name": "Dispositivo 1"},
            {"id": 2, "name": "Dispositivo 2"},
        ]
        return jsonify(devices), 200

    except Exception as e:
        print(f"[ERROR] Error en devices: {e}")
        return jsonify({"message": "Error interno en el servidor"}), 500

    finally:
        if conn:
            conn.close()  # Cerramos la conexión si fue inicializada correctamente

# Ruta para manejar login (ejemplo, ajusta según tu implementación actual)
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Conectar a la base de datos SQLite
        conn = sqlite3.connect('nueva_base.db')
        cursor = conn.cursor()

        # Verificar usuario
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "Credenciales inválidas"}), 401

        # Configurar la cookie
        response = jsonify({"message": "Inicio de sesión exitoso"})
        response.set_cookie('user_id', str(user[0]), httponly=True)
        return response, 200

    except Exception as e:
        print(f"[ERROR] Error en login: {e}")
        return jsonify({"message": "Error interno en el servidor"}), 500

    finally:
        if conn:
            conn.close()

# Ejecutar el servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
