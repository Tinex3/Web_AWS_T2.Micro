# Documentación Completa del Proyecto: Dashboard de Sensores en AWS EC2 (t2.micro)

## **Introducción**
Este documento explica todos los pasos necesarios para implementar un sistema de monitoreo de temperatura y humedad con una API y un dashboard web funcional. El proyecto utiliza Flask para el backend, SQLite como base de datos y un servidor AWS EC2 (t2.micro) para alojar todo.

---

## **1. Configuración Inicial en AWS**

### **1.1 Crear la Instancia EC2**
1. Inicia una instancia **t2.micro** desde la consola de AWS con:
   - **Sistema Operativo:** Amazon Linux 2 (u otro similar).
   - **Almacenamiento:** El predeterminado (8 GB suele ser suficiente).

2. Configura las **Reglas de Seguridad** para abrir los siguientes puertos:
   - **80 (HTTP):** Para el sitio web.
   - **8080:** Para el backend Flask.
   - **22 (SSH):** Para conectarte a la instancia.

### **1.2 Conectarte a la Instancia**
Conéctate a la instancia usando SSH:
```bash
ssh -i "tu_clave.pem" ec2-user@<dirección_IP_pública>
2. Configurar el Entorno en EC2
2.1 Instalar Dependencias Básicas
Actualizar el sistema:

bash
Copiar código
sudo yum update -y
Instalar Python y pip:

bash
Copiar código
sudo yum install python3 -y
sudo yum install python3-pip -y
Instalar SQLite:

bash
Copiar código
sudo yum install sqlite -y
2.2 Configurar un Entorno Virtual
Es recomendable usar un entorno virtual para manejar las dependencias del proyecto:

bash
Copiar código
python3 -m venv venv
source venv/bin/activate
2.3 Instalar Flask y Extensiones
Instala Flask y Flask-CORS dentro del entorno virtual:

bash
Copiar código
pip install flask flask-cors
3. Configurar la Base de Datos
3.1 Crear la Base de Datos SQLite
Crear una nueva base de datos:

bash
Copiar código
sqlite3 mi_base.db
Crear la tabla para almacenar los datos:

sql
Copiar código
CREATE TABLE mediciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sensor_id INTEGER NOT NULL,
    humedad REAL NOT NULL,
    temperatura REAL NOT NULL
);
Insertar datos de prueba (opcional):

sql
Copiar código
INSERT INTO mediciones (sensor_id, humedad, temperatura)
VALUES (1, 50.5, 22.3);
Sal de la consola SQLite:

bash
Copiar código
.exit
4. Configurar el Backend Flask
4.1 Crear el Archivo webserver.py
Crea el archivo principal del servidor backend y añade el siguiente código:

python
Copiar código
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = 'mi_base.db'

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/api/datos', methods=['GET'])
def obtener_datos():
    rows = query_db("SELECT * FROM mediciones ORDER BY timestamp DESC LIMIT 10")
    return jsonify([{'id': r[0], 'timestamp': r[1], 'sensor_id': r[2], 'humedad': r[3], 'temperatura': r[4]} for r in rows]), 200

@app.route('/')
def serve_dashboard():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
4.2 Ejecutar el Servidor
Ejecuta Flask en segundo plano:

bash
Copiar código
nohup python3 webserver.py > flask.log 2>&1 &
Revisa si el servidor está corriendo:

bash
Copiar código
curl http://localhost:8080/api/datos
5. Configurar el Frontend
5.1 Crear los Archivos del Frontend
Crea el archivo index.html: Contiene el código HTML para el dashboard:

html
Copiar código
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Sensores</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background-color: #f8f9fa;
        }
        .chart-container {
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center">Dashboard de Sensores</h1>
        <div class="row chart-container">
            <div class="col-md-6">
                <canvas id="temperatureChart"></canvas>
            </div>
            <div class="col-md-6">
                <canvas id="humidityChart"></canvas>
            </div>
        </div>
    </div>
    <script>
        // Código JavaScript para gráficos
    </script>
</body>
</html>
Subir los Archivos al Servidor EC2:

bash
Copiar código
scp -i "tu_clave.pem" index.html ec2-user@<tu_direccion_publica>:~/server/
6. Configurar el Dominio
6.1 Actualizar Reglas de Seguridad
Asegúrate de que los puertos 80, 8080 y 22 estén abiertos en las Reglas de Seguridad de tu instancia EC2.

6.2 Apuntar el Dominio
Configura un registro A en tu proveedor de dominio para apuntar a la IP pública de tu instancia EC2.

6.3 Ejecutar Flask en el Puerto 80
Edita el archivo webserver.py y cambia el puerto a 80:

python
Copiar código
app.run(host='0.0.0.0', port=80)
Ejecuta Flask con permisos sudo:

bash
Copiar código
sudo python3 webserver.py
7. Pruebas Finales
7.1 Verificar el Backend
Accede a la API:

bash
Copiar código
curl http://<tu_dominio>/api/datos
7.2 Verificar el Frontend
Abre tu navegador y accede a:

arduino
Copiar código
http://<tu_dominio>
8. Resumen de Comandos
Tarea	Comando
Actualizar el sistema	sudo yum update -y
Instalar Python y pip	sudo yum install python3 -y && sudo yum install python3-pip -y
Crear entorno virtual	python3 -m venv venv && source venv/bin/activate
Instalar Flask y CORS	pip install flask flask-cors
Crear base de datos SQLite	sqlite3 mi_base.db
Ejecutar Flask en segundo plano	nohup python3 webserver.py > flask.log 2>&1 &
Subir archivos al servidor	scp -i "tu_clave.pem" archivo ec2-user@<tu_ip>:~/server/
Logros Finales
API funcional: Proporciona datos desde SQLite.
Dashboard dinámico: Gráficos que se actualizan en tiempo real.
Infraestructura robusta: Migraste de Raspberry Pi a AWS EC2.
Dominio configurado: Tu aplicación es accesible desde http://<tu_dominio>.
go
Copiar código

Copia y pega este contenido en tu archivo `.md`. Si necesitas ajustes adicionales, ¡puedes pedírmelo! 🚀





