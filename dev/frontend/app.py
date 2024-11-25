from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia esto por una clave secreta

# Configuración de la API Backend
API_BASE_URL = "http://192.168.0.11:5000"

# Ruta para la página de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Llamada a la API para autenticar al usuario
        response = requests.post(f"{API_BASE_URL}/login", json={
            'username': username,
            'password': password
        })

        if response.status_code == 200:
            data = response.json()
            session['session_id'] = data['session_id']
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

# Ruta para el dashboard
@app.route('/dashboard')
def dashboard():
    if 'session_id' not in session:
        return redirect(url_for('login'))

    # Llamada a la API para obtener dispositivos
    devices_response = requests.get(f"{API_BASE_URL}/devices")
    devices = devices_response.json() if devices_response.status_code == 200 else []

    return render_template('dashboard.html', username=session['username'], devices=devices)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
