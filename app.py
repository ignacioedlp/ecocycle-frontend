from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from helpers.authentication_bonita import authentication  # Corrige la importación
from helpers.tomar_reserva import tomar_reserva_bonita
from helpers.completar_reserva import completar_reserva_bonita
from models.models import *
from database import db  
from models.models import Material, DepositoComunal, Recoleccion # Asegúrate de importar los modelos

import requests
import jwt
import os
from helpers.add_recoleccion import (
    add_recoleccion
)
from helpers.create_reserva import (
    create_reserva
)
from helpers.finish_recoleccion import (
    finish_recoleccion
)
from helpers.get_reservas import get_reservas

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')  # Cambia esta clave por una segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ecocycleadmin:password@db:5432/ecocycle'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
JWT_SECRET_KEY  = os.environ.get('JWT_SECRET_KEY')   # Cambia esta clave por una segura
API_URL = os.environ.get('API_URL')
db.init_app(app)
migrate = Migrate(app, db)

def get_user_info():
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    role_name = session.get('role_name')
    print(f"role {role_name}")

    if user_id:
        return user_id, user_name, role_name
    else:
        return None, None, None

# Ruta para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    print(request.method)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Realiza la petición al endpoint de login en tu API
        response = authentication(username, password)
        
        if response:
            return redirect(url_for('create_recoleccion'))
        else:
            return 'Login failed: No access token in response', 401

    return render_template('login.html')

# Ruta protegida para crear recolección
@app.route('/create-recoleccion', methods=['GET', 'POST'])
def create_recoleccion():
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Recolector'
    if role_name != 'Recolector':
        return 'No autorizado: Necesitas ser Recolector', 403
            
    # Obtener materiales y depósitos desde la base de datos local
    materiales = Material.query.all()  # Consulta para obtener todos los materiales
    depositos = DepositoComunal.query.all()  # Consulta para obtener todos los depósitos
    
    if request.method == 'POST':
        material_id = request.form['material']
        deposito_id = request.form['deposito']
        cantidad = request.form['cantidad']
        
        # Enviar los datos de la recolección a tu API
        data = {
            'material_id': material_id,
            'deposito_id': deposito_id,
            'cantidad': cantidad
        }
        case_id = add_recoleccion(material_id, cantidad, deposito_id)
        
        if case_id:
            return f"Recolección creada con éxito, su caso es: {case_id}", 200
        else:
            return 'Error al crear la recolección', 400
    
    return render_template('create_recoleccion.html', materiales=materiales, depositos=depositos)

# Ruta para mostrar la tabla de recolecciones
@app.route('/recolecciones')
def mostrar_recolecciones():
    user_id, user_name, role_name = get_user_info()

    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return 'No autorizado: Necesitas ser Empleado', 403
        
    # Obtener las órdenes de la API de Cloud que esten pendientes
    recolecciones = Recoleccion.query.filter_by(estado='pendiente').all()
    
    return render_template('recolecciones.html', recolecciones=recolecciones)

# Ruta para actualizar la orden
@app.route('/actualizar-orden/<int:id>', methods=['POST'])
def actualizar_orden(id):
    user_id, user_name, role_name = get_user_info()

    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return 'No autorizado: Necesitas ser Empleado', 403
        
    cantidad_final = request.form['cantidad_final']
    
    # Hacer el PUT a la API de Cloud para actualizar la orden
    result = finish_recoleccion(id, cantidad_final)
        
    if result:
        return f"Recolección actualizada con éxito.", 200
    else:
        return 'Error al actualizar la recolección', 400
    
@app.route('/reservar-material', methods=['POST', 'GET'])
def reservar_material():
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Fabricante'
    if role_name != 'Fabricante':
        return 'No autorizado: Necesitas ser Fabricante', 403
        
    materiales = Material.query.all()  # Consulta para obtener todos los materiales

    if request.method == 'POST':
        material_id = request.form['material']
        cantidad = request.form['cantidad']
        fecha_prevista = request.form['fecha_reserva']

        case_id = create_reserva(cantidad, material_id, fecha_prevista)
        
        if case_id:
            return f"Reserva creada con éxito, su caso es: {case_id}", 200
        else:
            return 'Error al crear la Reserva', 400
        

    return render_template('reservar.html', materiales=materiales)

@app.route('/reservas-pendientes', methods=['POST', 'GET'])
def reservas_pendientes():
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return 'No autorizado: Necesitas ser Empleado', 403
        
    materiales = Material.query.all()  # Consulta para obtener todos los materiales
    depositos = DepositoComunal.query.all()
    return render_template('reservas-pendientes.html', materiales=materiales, depositos=depositos)

@app.route('/consultar-reservas', methods=['GET'])
def consultar_reservas():
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return 'No autorizado: Necesitas ser Empleado', 403
    
    material_id = request.args.get('material_id')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    return get_reservas(fecha_inicio, fecha_fin, material_id)



@app.route('/tomar-reserva/<int:reserva_id>', methods=['POST'])
def tomar_reserva(reserva_id):
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return 'No autorizado: Necesitas ser Empleado', 403
    # Aquí procesas la solicitud para tomar la reserva
    # Por ejemplo, puedes actualizar el estado de la reserva en la base de datos
    deposito_id = request.args.get('deposito_id')

    tomar_reserva_bonita(reserva_id, deposito_id)
    
    return jsonify({'message': 'Reserva tomada con éxito'}), 200


@app.route('/completar-reserva/<int:reserva_id>', methods=['POST'])
def completar_reserva(reserva_id):
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return 'No autorizado: Necesitas ser Empleado', 403

    # TODO: aca deberiamos verificar el stock y actualizarla en tal caso
    completar_reserva_bonita(reserva_id)

    
    return jsonify({'message': 'Reserva tomada con éxito'}), 200


@app.route('/api/recolecciones', methods=['POST'])
def api_create_recoleccion():            

    if request.method == 'POST':
        material_id = request.form['material_id']
        deposito_id = request.form['deposito_id']
        cantidad = request.form['cantidad']
        
        # Crear una recolección
        recoleccion = Recoleccion(material_id=material_id, deposito_id=deposito_id, cantidad_inicial=cantidad)
        db.session.add(recoleccion)
        db.session.commit()
        
        if recoleccion.id:
            return {id: recoleccion.id}, 200
        else:
            return 'Error al crear la recolección', 400

@app.route('/api/recolecciones/<int:recoleccion_id>', methods=['PUT'])
def api_finalizar_recoleccion(recoleccion_id):            

    if request.method == 'PUT':
        cantidad_final = request.form['cantidad_final']
        
        recoleccion = Recoleccion.query.get(recoleccion_id)
        recoleccion.cantidad_final = cantidad_final
        db.session.commit()
        
        if recoleccion.id:
            return {id: recoleccion.id}, 200
        else:
            return 'Error al crear la recolección', 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.secret_key = os.environ.get('JWT_SECRET_KEY')  # Cambia esta clave por una segura
    app.run(host='0.0.0.0', port=5000, debug=True)
