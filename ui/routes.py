from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from helpers.completar_reserva import completar_reserva_bonita
from helpers.create_reserva import create_reserva
from helpers.finish_recoleccion import finish_recoleccion
from helpers.get_reservas import get_reservas
from helpers.tomar_reserva import tomar_reserva_bonita
from models.models import Material, DepositoComunal, Recoleccion, PuntoDeRecoleccion, Stock
from helpers.add_recoleccion import add_recoleccion
from helpers.authentication_bonita import authentication_bonita

def get_user_info():
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    role_name = session.get('role_name')

    if user_id:
        return user_id, user_name, role_name
    else:
        return None, None, None

ui = Blueprint('ui', __name__)

# Ruta para login
@ui.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Realiza la petición al endpoint de login en tu API
        response = authentication_bonita(username, password)
        
        if response:
            return redirect(url_for('ui.home'))
        else:
            return 'Login failed: No access token in response', 401

    return render_template('login.html')

# Ruta para mostrar la tabla de recolecciones
@ui.route('/recolecciones')
def mostrar_recolecciones():
    user_id, user_name, role_name = get_user_info()

    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return render_template('unauthorized.html'), 403
        
    # Obtener las órdenes de la API de Cloud que esten pendientes
    recolecciones = Recoleccion.query.filter_by(estado='Pendiente').all()
    
    return render_template('recolecciones.html', recolecciones=recolecciones, user_id=user_id)

# Ruta protegida para crear recolección
@ui.route('/crear-recoleccion', methods=['GET', 'POST'])
def create_recoleccion():
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Recolector'
    if role_name != 'Recolector':
        return render_template('unauthorized.html'), 403
            
    # Obtener materiales y depósitos desde la base de datos local
    materiales = Material.query.all()  # Consulta para obtener todos los materiales
    depositos = DepositoComunal.query.all()  # Consulta para obtener todos los depósitos
    puntos = PuntoDeRecoleccion.query.all()
    
    if request.method == 'POST':
        material_id = request.form['material']
        deposito_id = request.form['deposito']
        cantidad = request.form['cantidad']
        punto_de_recoleccion_id =request.form['punto_de_recoleccion']
        
        # Enviar los datos de la recolección a tu API
        case_id = add_recoleccion(material_id, cantidad, deposito_id, punto_de_recoleccion_id)
        
        if case_id:
            return f"Recolección creada con éxito, su caso es: {case_id}", 200
        else:
            return 'Error al crear la recolección', 400
    
    return render_template('create_recoleccion.html', materiales=materiales, depositos=depositos, puntos=puntos, user_id=user_id)

# Ruta para actualizar la orden
@ui.route('/completar-recoleccion/<int:id>', methods=['POST'])
def actualizar_orden(id):
    user_id, user_name, role_name = get_user_info()

    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return render_template('unauthorized.html'), 403
        
    cantidad_final = request.form['cantidad_final']
    
    # Hacer el PUT a la API de Cloud para actualizar la orden
    result = finish_recoleccion(id, cantidad_final)
        
    if result:
        return f"Recolección actualizada con éxito.", 200
    else:
        return 'Error al actualizar la recolección', 400
    
@ui.route('/reservar-material', methods=['POST', 'GET'])
def reservar_material():
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Fabricante'
    if role_name != 'Fabricante':
        return render_template('unauthorized.html'), 403
        
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

@ui.route('/reservas-pendientes', methods=['POST', 'GET'])
def reservas_pendientes():
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return render_template('unauthorized.html'), 403
        
    materiales = Material.query.all()  # Consulta para obtener todos los materiales
    depositos = DepositoComunal.query.all()

    materiales_json = [{'id': m.id, 'name': m.name} for m in materiales]
    depositos_json = [{'id': d.id, 'name': d.name} for d in depositos]
    return render_template('reservas-pendientes.html', materiales=materiales_json, depositos=depositos_json, user_id=user_id)

@ui.route('/', methods=['GET'])
def home():
    user_id, user_name, role_name = get_user_info()
    return render_template('home.html', user_id=user_id)

@ui.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Elimina todos los datos de la sesión
    user_id, user_name, role_name = get_user_info()
    return render_template('home.html', user_id=user_id)

@ui.route('/ingresar-sorteo')
def sorteo():
    user_id, user_name, role_name = get_user_info()

        # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Punto':
        return render_template('unauthorized.html'), 403
    
    return render_template('ingresar-sorteo.html', user_id=user_id)