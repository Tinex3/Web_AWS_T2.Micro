from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import sqlite3
app = Flask(__name__, template_folder='templates')  # Asegúrate de tener la carpeta 'templates' para HTML
CORS(app)  # Habilitar CORS para el acceso desde otros orígenes
DATABASE = 'nueva_base.db'

def query_db(query, args=(), one=False):
    """
    Función para interactuar con la base de datos SQLite.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    """
    Ruta principal que sirve la página web con el dashboard.
    """
    dispositivos = query_db("SELECT * FROM dispositivos")
    return render_template('index.html', dispositivos=dispositivos)

@app.route('/api/datos', methods=['GET'])
def obtener_datos():
    """
    Endpoint para obtener las mediciones de un dispositivo específico.
    """
    sensor_id = request.args.get('sensor_id')
    if not sensor_id:
        return jsonify({'error': 'El parámetro sensor_id es obligatorio'}), 400

    try:
        mediciones = query_db(
            "SELECT * FROM mediciones WHERE id_dispositivo = ? ORDER BY timestamp DESC LIMIT 50",
            (sensor_id,)
        )
        return jsonify([
            {
                'id': m[0],
                'timestamp': m[1],
                'id_dispositivo': m[2],
                'temperatura': m[3],
                'humedad': m[4],
                'distancia': m[5],
                'valor_random': m[6]
            } for m in mediciones
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)