from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = 'nueva_base.db'  # Nombre de tu base de datos

def query_db(query, args=(), one=False):
    """Función para interactuar con la base de datos SQLite"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchall()
    conn.close()
    return (result[0] if result else None) if one else result

@app.route('/api/user-count', methods=['GET'])
def user_count():
    """Devuelve el número total de usuarios registrados"""
    try:
        query = "SELECT COUNT(*) FROM users;"  # Asegúrate de que la tabla se llama 'users'
        count = query_db(query, one=True)[0]
        return jsonify({"user_count": count}), 200
    except Exception as e:
        return jsonify({"message": "Error al contar usuarios", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
