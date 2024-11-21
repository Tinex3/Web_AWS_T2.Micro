from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import timedelta

# Configuración de la app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///production.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_production_jwt_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "*"}})

# Modelos de la base de datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), default="User")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)

class Device(db.Model):
    device_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_name = db.Column(db.String(120), nullable=False)
    device_type = db.Column(db.String(50))
    status = db.Column(db.String(50), default="activo")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref=db.backref('devices', lazy=True))

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

# Rutas para servir páginas web
@app.route('/')
def home():
    """Ruta principal que muestra el login"""
    return render_template('index.html')

@app.route('/dashboard')
@jwt_required()
def dashboard():
    """Ruta para mostrar el dashboard del usuario"""
    current_user = get_jwt_identity()
    devices = Device.query.filter_by(user_id=current_user['id']).all()
    return render_template('dashboard.html', devices=devices)

# Endpoints RESTful

@app.route('/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario"""
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password, email=data['email'])
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Usuario registrado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al registrar usuario", "error": str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    """Autenticar un usuario y devolver un token JWT"""
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={"id": user.id, "role": user.role})
        return jsonify({"access_token": access_token}), 200
    return jsonify({"message": "Credenciales inválidas"}), 401

@app.route('/devices', methods=['GET'])
@jwt_required()
def get_devices():
    """Obtener dispositivos del usuario autenticado"""
    current_user = get_jwt_identity()
    devices = Device.query.filter_by(user_id=current_user['id']).all()
    return jsonify([{
        "device_id": d.device_id,
        "device_name": d.device_name,
        "status": d.status
    } for d in devices]), 200

@app.route('/devices/add', methods=['POST'])
@jwt_required()
def add_device():
    """Agregar un dispositivo para el usuario autenticado"""
    current_user = get_jwt_identity()
    data = request.json
    new_device = Device(
        user_id=current_user['id'],
        device_name=data['device_name'],
        device_type=data.get('device_type', 'unknown'),
        status=data.get('status', 'activo')
    )
    try:
        db.session.add(new_device)
        db.session.commit()
        return jsonify({"message": "Dispositivo añadido exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al añadir dispositivo", "error": str(e)}), 400

@app.route('/assign-role', methods=['POST'])
@jwt_required()
def assign_role():
    """Asignar un rol a un usuario (solo admin)"""
    current_user = get_jwt_identity()
    if current_user['role'] != 'Admin':
        return jsonify({"message": "No autorizado"}), 403

    data = request.json
    user = User.query.get(data['user_id'])
    if user:
        user.role = data['role']
        try:
            db.session.commit()
            return jsonify({"message": f"Rol asignado a {user.username} como {user.role}"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error al asignar rol", "error": str(e)}), 400
    return jsonify({"message": "Usuario no encontrado"}), 404

@app.route('/sensor-status', methods=['GET'])
@jwt_required()
def sensor_status():
    """Obtener el estado de los sensores asociados al usuario autenticado"""
    current_user = get_jwt_identity()
    devices = Device.query.filter_by(user_id=current_user['id']).all()
    return jsonify([{
        "device_id": device.device_id,
        "device_name": device.device_name,
        "status": device.status
    } for device in devices]), 200

@app.route('/register-page')
def register_page():
    """Ruta para la página de registro"""
    return render_template('register.html')


# Ejecutar el servidor
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
