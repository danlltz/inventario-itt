from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE LA BASE DE DATOS EN LA NUBE (CLEVER CLOUD) ---
# He usado los datos de tu captura de pantalla
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

# Crear las tablas automáticamente en la nube
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

@app.route('/equipos', methods=['GET'])
def obtener_equipos():
    return jsonify([{"id":e.id,"nombre":e.nombre,"descripcion":e.descripcion,"cantidad":e.cantidad,"operativos":e.operativos,"ubicacion":e.ubicacion,"tipo":e.tipo,"estado":e.estado} for e in Equipo.query.all()])

@app.route('/agregar', methods=['POST'])
def agregar():
    d = request.json
    nuevo = Equipo(nombre=d['nombre'], descripcion=d.get('descripcion'), cantidad=d['cantidad'], operativos=d.get('operativos'), ubicacion=d['ubicacion'], tipo=d['tipo'], estado=d['estado'])
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"m":"ok"})

@app.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    e = Equipo.query.get(id)
    if e: db.session.delete(e); db.session.commit()
    return jsonify({"m":"ok"})

@app.route('/laboratorios', methods=['GET', 'POST'])
def manejar_labs():
    if request.method == 'POST':
        db.session.add(Laboratorio(nombre=request.json.get('nombre')))
        db.session.commit()
        return jsonify({"m":"ok"})
    return jsonify([{"id":l.id, "nombre":l.nombre} for l in Laboratorio.query.all()])

@app.route('/laboratorios/<int:id>', methods=['DELETE'])
def borrar_lab(id):
    l = Laboratorio.query.get(id)
    if l: db.session.delete(l); db.session.commit()
    return jsonify({"m":"ok"})

if __name__ == '__main__':
    # Render usará la variable de entorno PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
