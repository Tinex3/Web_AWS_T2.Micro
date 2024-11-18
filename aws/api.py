from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import logging

# Configuración básica de la app Flask
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Configuración de CORS

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE = 'nueva_base.db'

# Función para conectarse a la base de datos
def query_db(query, args=(), one=False, many=False):
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if many:
            cursor.executemany(query, args)
        else:
            cursor.execute(query, args)

        if query.strip().upper().startswith("SELECT"):
            rv = cursor.fetchall()
            return (rv[0] if rv else None) if one else rv
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error de SQLite: {e}")
        raise
    finally:
        conn.close()

# Endpoint para manejar dispositivos
@app.route('/api/dispositivos', methods=['GET', 'POST', 'DELETE'])
def manejar_dispositivos():
    if request.method == 'GET':
        try:
            dispositivos = query_db("SELECT * FROM dispositivos")
            dispositivos = [
                {'id': d['id'], 'nombre': d['nombre'], 'tipo_datos': d['tipo_datos']}
                for d in dispositivos
            ]
            return jsonify(dispositivos), 200
        except Exception as e:
            logging.error(f"Error al obtener dispositivos: {str(e)}")
            return jsonify({'error': 'Error al obtener dispositivos', 'detalles': str(e)}), 500

    elif request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({'error': 'El cuerpo de la solicitud no puede estar vacío'}), 400

        if not isinstance(data, list):
            data = [data]

        sensores = []
        for sensor in data:
            sensor_id = sensor.get('id')
            nombre = sensor.get('nombre')
            tipo_datos = sensor.get('tipo_datos')

            if not all([nombre, tipo_datos]):
                return jsonify({'error': 'Cada sensor debe tener nombre y tipo_datos'}), 400

            sensores.append((sensor_id, nombre, tipo_datos))

        try:
            query_db(
                "INSERT INTO dispositivos (id, nombre, tipo_datos) VALUES (?, ?, ?)",
                args=sensores,
                many=True
            )
            return jsonify({'status': 'success', 'message': f'{len(sensores)} dispositivos insertados correctamente'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'ID duplicado o conflicto con la base de datos'}), 409
        except Exception as e:
            logging.error(f"Error al insertar dispositivos: {str(e)}")
            return jsonify({'error': 'Error al insertar dispositivos', 'detalles': str(e)}), 500

    elif request.method == 'DELETE':
        dispositivo_id = request.args.get('id')

        try:
            if dispositivo_id:
                query_db("DELETE FROM dispositivos WHERE id = ?", (dispositivo_id,))
                return jsonify({'status': 'success', 'message': f'Dispositivo con ID {dispositivo_id} eliminado'}), 200
            else:
                query_db("DELETE FROM dispositivos")
                return jsonify({'status': 'success', 'message': 'Todos los dispositivos han sido eliminados'}), 200
        except Exception as e:
            logging.error(f"Error al eliminar dispositivos: {str(e)}")
            return jsonify({'error': 'Error al eliminar dispositivos', 'detalles': str(e)}), 500

# Endpoint para manejar mediciones
@app.route('/api/mediciones', methods=['GET', 'POST'])
def manejar_mediciones():
    if request.method == 'GET':
        sensor_id = request.args.get('sensor_id')
        if not sensor_id:
            return jsonify({'error': 'El parámetro sensor_id es obligatorio'}), 400

        try:
            mediciones = query_db(
                "SELECT * FROM mediciones WHERE id_dispositivo = ? ORDER BY timestamp DESC",
                (sensor_id,)
            )

            if not mediciones:
                return jsonify([]), 200

            mediciones = [
                {
                    'id': m['id'],
                    'id_dispositivo': m['id_dispositivo'],
                    'timestamp': m['timestamp'],
                    'temperatura': m['temperatura'],
                    'humedad': m['humedad'],
                    'distancia': m['distancia'],
                    'valor_random': m['valor_random'],
                }
                for m in mediciones
            ]
            return jsonify(mediciones), 200
        except Exception as e:
            logging.error(f"Error al obtener mediciones: {str(e)}")
            return jsonify({'error': 'Error al obtener mediciones', 'detalles': str(e)}), 500

    elif request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({'error': 'El cuerpo de la solicitud no puede estar vacío'}), 400

        id_dispositivo = data.get('id_dispositivo')
        temperatura = data.get('temperatura')
        humedad = data.get('humedad')
        distancia = data.get('distancia')
        valor_random = data.get('valor_random')

        if not id_dispositivo:
            return jsonify({'error': 'El campo id_dispositivo es obligatorio'}), 400

        try:
            dispositivo = query_db(
                "SELECT * FROM dispositivos WHERE id = ?", (id_dispositivo,), one=True
            )

            if not dispositivo:
                return jsonify({'error': 'Dispositivo no encontrado'}), 404

            query_db(
                """
                INSERT INTO mediciones (id_dispositivo, temperatura, humedad, distancia, valor_random)
                VALUES (?, ?, ?, ?, ?)
                """,
                (id_dispositivo, temperatura, humedad, distancia, valor_random)
            )
            return jsonify({'status': 'success', 'message': 'Medición insertada correctamente'}), 201
        except Exception as e:
            logging.error(f"Error al insertar medición: {str(e)}")
            return jsonify({'error': 'Error al insertar medición', 'detalles': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
