import requests
from flask import Flask, render_template, request, jsonify, redirect, session

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'development_secret_key'

# Rutas para servir páginas web
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register-page')
def register_page():
    return render_template('register.html')

@app.route('/blank')
def blank():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('blank.html')

@app.route('/dashboard')
def dashboard():
    """Renderiza el dashboard para el usuario autenticado"""
    if 'user_id' not in session:
        return redirect('/')  # Redirige al login si no hay sesión
    try:
        # Enviar solicitud al endpoint /devices con cookies
        response = requests.get("http://127.0.0.1:5000/devices", cookies=request.cookies)

        if response.status_code == 200:
            devices = response.json()
            return render_template("dashboard.html", devices=devices)
        else:
            print(f"[ERROR] Error al obtener dispositivos: {response.status_code} - {response.text}")
            return redirect('/')  # Redirige al login en caso de error

    except Exception as e:
        print(f"[ERROR] Error en el dashboard: {e}")
        return "Error interno del servidor", 500


# Rutas para procesar solicitudes de la API
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        response = requests.post('http://127.0.0.1:5000/login', json=data)

        if response.status_code == 200:
            session['user_id'] = response.cookies.get('user_id')
            return jsonify({"message": "Inicio de sesión exitoso", "redirect_url": "/blank"}), 200
        else:
            return jsonify({"message": response.json().get("message", "Error al iniciar sesión")}), response.status_code
    except Exception as e:
        print(f"[ERROR] Error en login: {e}")
        return jsonify({"message": "Error interno en el servidor"}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Sesión cerrada exitosamente"}), 200

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        response = requests.post('http://127.0.0.1:5000/register', json=data)

        if response.status_code == 201:
            return jsonify({"message": "Registro exitoso", "redirect_url": "/"}), 201
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"[ERROR] Error en registro: {e}")
        return jsonify({"message": "Error interno en el servidor"}), 500

# Ejecutar el servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
