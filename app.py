from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
# Habilitamos CORS para que tu frontend pueda comunicarse con el backend sin bloqueos
CORS(app)

# --- CONFIGURACIÓN DE LA BASE DE DATOS EN LA NUBE (CLEVER CLOUD) ---
DB_USER = "umxecnhtmv1r1pek"
DB_PASS = "sw925d7pO4cACXkhbppS"
DB_HOST = "br9qvi6nvfv8mled1zqu-mysql.services.clever-cloud.com"
DB_NAME = "br9qvi6nvfv8mled1zqu"

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS ---
class Equipo(db.Model):
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    cantidad = db.Column(db.Integer, default=1)
    operativos = db.Column(db.Integer, default=1)
    ubicacion = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    estado = db.Column(db.String(50))

class Laboratorio(db.Model):
    __tablename__ = 'laboratorios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(255), nullable=False)

# Crea las tablas si no existen al iniciar
with app.app_context():
    db.create_all()

# --- RUTAS ---

@app.route('/login', methods=['POST'])
def login():
    datos = request.json
    usuario = Usuario.query.get(datos.get('user'))
    if usuario and usuario.password == str(datos.get('pass')):
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/cambiar-password', methods=['POST'])
def cambiar_password():
    datos = request.json
    usuario_id = datos.get('user')
    clave_vieja = str(datos.get('old_pass'))
    clave_nueva = str(datos.get('new_pass'))

    # Buscamos al usuario por su ID (nombre de usuario)
    usuario = Usuario.query.get(usuario_id)

    if usuario and usuario.password == clave_vieja:
        usuario.password = clave_nueva
        db.session.commit()  # IMPORTANTE: Guarda los cambios en MariaDB
        return jsonify({"success": True, "m": "Clave actualizada con éxito"})
    
    return jsonify({"success": False, "m": "La clave actual es incorrecta"}), 401

@app.route('/equipos', methods=['GET'])
def obtener_equipos():
    equipos = Equipo.query.all()
    return jsonify([{
        "id": e.id,
        "nombre": e.nombre,
        "descripcion": e.descripcion,
        "cantidad": e.cantidad,
        "operativos": e.operativos,
        "ubicacion": e.ubicacion,
        "tipo": e.tipo,
        "estado": e.estado
    } for e in equipos])

@app.route('/agregar', methods=['POST'])
def agregar():
    d = request.json
    try:
        if int(d['cantidad']) < 0 or int(d.get('operativos', 0)) < 0:
            return jsonify({"error": "No se permiten valores negativos"}), 400
        if int(d.get('operativos', 0)) > int(d['cantidad']):
            return jsonify({"error": "Funcionando no puede ser mayor al total"}), 400

        nuevo = Equipo(
            nombre=d['nombre'], 
            descripcion=d.get('descripcion'), 
            cantidad=d['cantidad'], 
            operativos=d.get('operativos'), 
            ubicacion=d['ubicacion'], 
            tipo=d['tipo'], 
            estado=d['estado']
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"m": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/editar/<int:id>', methods=['PUT'])
def editar(id):
    d = request.json
    e = Equipo.query.get(id)
    if not e: 
        return jsonify({"m": "no encontrado"}), 404
    
    if int(d['cantidad']) < 0 or int(d.get('operativos', 0)) < 0:
        return jsonify({"error": "No negativos"}), 400
    if int(d.get('operativos', 0)) > int(d['cantidad']):
        return jsonify({"error": "Operativos mayor al total"}), 400

    e.nombre = d['nombre']
    e.descripcion = d.get('descripcion')
    e.cantidad = d['cantidad']
    e.operativos = d['operativos']
    e.ubicacion = d['ubicacion']
    e.tipo = d['tipo']
    e.estado = d['estado']
    db.session.commit()
    return jsonify({"m": "ok"})

@app.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    e = Equipo.query.get(id)
    if e: 
        db.session.delete(e)
        db.session.commit()
    return jsonify({"m": "ok"})

@app.route('/laboratorios', methods=['GET', 'POST'])
def manejar_labs():
    if request.method == 'POST':
        nombre_lab = request.json.get('nombre')
        if nombre_lab:
            db.session.add(Laboratorio(nombre=nombre_lab))
            db.session.commit()
            return jsonify({"m": "ok"})
    labs = Laboratorio.query.all()
    return jsonify([{"id": l.id, "nombre": l.nombre} for l in labs])

@app.route('/laboratorios/<int:id>', methods=['DELETE'])
def borrar_lab(id):
    l = Laboratorio.query.get(id)
    if l: 
        db.session.delete(l)
        db.session.commit()
    return jsonify({"m": "ok"})

if __name__ == '__main__':
    # Configuración para despliegue en Render u otros servicios
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
