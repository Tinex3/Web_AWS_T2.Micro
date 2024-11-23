import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

# Configuración de la app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JWT_SECRET_KEY'] = 'your_production_jwt_secret_key'  # Cambia esto a un valor seguro
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
jwt = JWTManager(app)

# Rutas para servir páginas web
@app.route('/')
def home():
    """Página principal de inicio de sesión"""
    return render_template('index.html')

@app.route('/register-page', methods=['GET'])
def register_page():
    """Página de registro"""
    return render_template('register.html')

@app.route('/dashboard')
@jwt_required()
def dashboard():
    """Renderiza el dashboard para el usuario autenticado"""
    try:
        # Obtener la identidad actual (usuario autenticado)
        current_identity = get_jwt_identity()
        print(f"Usuario autenticado: {current_identity}")

        # Generar el token JWT desde la identidad actual
        token = create_access_token(identity=current_identity)

        # Enviar solicitud al endpoint /devices en api.py con el token JWT
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://127.0.0.1:5000/devices", headers=headers)

        if response.status_code == 200:
            # Si la respuesta es una lista, la procesamos directamente
            devices = response.json()
            return render_template("dashboard.html", devices=devices)
        else:
            print(f"Error al obtener dispositivos: {response.status_code} - {response.text}")
            return f"Error al obtener dispositivos: {response.status_code} - {response.text}", response.status_code

    except Exception as e:
        print(f"Error en el dashboard: {e}")
        return "Error interno del servidor", 500


# Rutas para procesar solicitudes de la API
@app.route('/login', methods=['POST'])
def login():
    """Enviar credenciales al endpoint /login de la API y redirigir al dashboard"""
    try:
        data = request.json
        response = requests.post('http://127.0.0.1:5000/login', json=data)

        if response.status_code == 200:
            # Login exitoso
            token = response.json().get("access_token")
            if token:
                # Redirigir al dashboard con el token
                return jsonify({"message": "Inicio de sesión exitoso", "redirect_url": "/dashboard", "token": token}), 200
            else:
                return jsonify({"message": "Error: No se recibió el token"}), 500
        else:
            # Manejar errores de login
            return jsonify({"message": response.json().get("message", "Error al iniciar sesión")}), response.status_code

    except Exception as e:
        print(f"Error en el inicio de sesión: {e}")
        return jsonify({"message": "Error interno del servidor", "error": str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    """Enviar los datos de registro al endpoint /register de la API"""
    try:
        data = request.json
        response = requests.post('http://127.0.0.1:5000/register', json=data)

        if response.status_code == 201:
            return jsonify({"message": "Registro exitoso", "redirect_url": "/"}), 201
        else:
            return jsonify({"message": response.json().get("message", "Error al registrar usuario")}), response.status_code

    except Exception as e:
        print(f"Error en el registro: {e}")
        return jsonify({"message": "Error interno del servidor", "error": str(e)}), 500

# Ejecutar el servidor
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
