from flask import Flask, render_template, request, redirect, url_for, jsonify, session

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

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')  # Cambia esta clave por una segura
JWT_SECRET_KEY  = os.environ.get('JWT_SECRET_KEY')   # Cambia esta clave por una segura
API_URL = os.environ.get('API_URL')

def decode_jwt_token():
    token = session.get('jwt_token')
    if not token:
        return None, 'No token found'
    
    try:
        print('print', JWT_SECRET_KEY)
        # Decodificar el token usando la clave secreta y sin verificar la firma (opcional)
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        
        # Extraer los grupos del token decodificado
        groups = decoded_token.get('groups', [])
        user_id = decoded_token.get('user_id', None)
        return groups, user_id, None
    except jwt.ExpiredSignatureError:
        return None, None, 'Token has expired'
    except jwt.InvalidTokenError:
        return None, None, 'Invalid token'

# Ruta para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    print(request.method)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Realiza la petición al endpoint de login en tu API
        response = requests.post(f"{API_URL}/login/", json={
            'username': username, 
            'password': password
        })
        
        if response.status_code == 200:
            tokens = response.json()  # Obtener tanto access como refresh token
            access_token = tokens.get('access')  # Obtener el token de access
            if access_token:
                session['jwt_token'] = access_token  # Almacena el token de access en la sesión
                return redirect(url_for('create_recoleccion'))
            else:
                return 'Login failed: No access token in response', 401
        else:
            return 'Login failed', 401
    return render_template('login.html')

# Ruta protegida para crear recolección
@app.route('/create-recoleccion', methods=['GET', 'POST'])
def create_recoleccion():
    groups, user_id, error = decode_jwt_token()
    
    if error:
        return error, 401
    
    # Verificar si el usuario tiene el grupo 'Recolector'
    if 'Recolector' not in groups:
        return 'No autorizado: Necesitas ser Recolector', 403
        
    token = session.get('jwt_token')  # Usa el token de access en la cabecera
    headers = {'Authorization': f'Bearer {token}'}  # Usa el token en la cabecera
    
    materiales = requests.get(f"{API_URL}/materiales/", headers=headers).json()
    depositos = requests.get(f"{API_URL}/depositos-comunales/", headers=headers).json()
    
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
        case_id = add_recoleccion(token, user_id, material_id, cantidad, deposito_id)
        
        if case_id:
            return f"Recolección creada con éxito, su caso es: {case_id}", 200
        else:
            return 'Error al crear la recolección', 400
    
    return render_template('create_recoleccion.html', materiales=materiales, depositos=depositos)

# Ruta para mostrar la tabla de recolecciones
@app.route('/recolecciones')
def mostrar_recolecciones():
    groups, user_id, error = decode_jwt_token()
    
    if error:
        return error, 401
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if 'Empleado' not in groups:
        return 'No autorizado: Necesitas ser Empleado', 403
        
    token = session.get('jwt_token')  # Usa el token de access en la cabecera
    headers = {'Authorization': f'Bearer {token}'}  # Usa el token en la cabecera

    # Obtener las órdenes de la API de Cloud
    ordenes = requests.get(f'{API_URL}/ordenes', headers=headers).json()
    
    return render_template('recolecciones.html', recolecciones=ordenes)

# Ruta para actualizar la orden
@app.route('/actualizar-orden/<int:id>', methods=['POST'])
def actualizar_orden(id):
    groups, user_id, error = decode_jwt_token()
    
    if error:
        return error, 401
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if 'Empleado' not in groups:
        return 'No autorizado: Necesitas ser Empleado', 403
        
    token = session.get('jwt_token')  # Usa el token de access en la cabecera
    headers = {'Authorization': f'Bearer {token}'}  # Usa el token en la cabecera

    cantidad_final = request.form['cantidad_final']
    
    # Hacer el PUT a la API de Cloud para actualizar la orden
    result = finish_recoleccion(token, id, cantidad_final)
        
    if result:
        return f"Recolección actualizada con éxito.", 200
    else:
        return 'Error al actualizar la recolección', 400
    
@app.route('/reservar-material', methods=['POST', 'GET'])
def reservar_material():
    groups, user_id, error = decode_jwt_token()
    
    if error:
        return error, 401
    
    # Verificar si el usuario tiene el grupo 'Fabricante'
    if 'Fabricante' not in groups:
        return 'No autorizado: Necesitas ser Fabricante', 403
        
    token = session.get('jwt_token')  # Usa el token de access en la cabecera
    headers = {'Authorization': f'Bearer {token}'}  # Usa el token en la cabecera
    materiales = requests.get(f"{API_URL}/materiales/", headers=headers).json()

    if request.method == 'POST':
        material_id = request.form['material']
        cantidad = request.form['cantidad']
        fecha_prevista = request.form['fecha_reserva']

        case_id = create_reserva(token, cantidad, material_id, fecha_prevista)
        
        if case_id:
            return f"Reserva creada con éxito, su caso es: {case_id}", 200
        else:
            return 'Error al crear la Reserva', 400
        

    return render_template('reservar.html', materiales=materiales)

@app.route('/reservas-pendientes', methods=['POST', 'GET'])
def reservas_pendientes():
    groups, user_id, error = decode_jwt_token()
    
    if error:
        return error, 401
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if 'Empleado' not in groups:
        return 'No autorizado: Necesitas ser Empleado', 403
        
    token = session.get('jwt_token')  # Usa el token de access en la cabecera
    headers = {'Authorization': f'Bearer {token}'}  # Usa el token en la cabecera
    materiales = requests.get(f"{API_URL}/materiales/", headers=headers).json()

    return render_template('reservas-pendientes.html', materiales=materiales)


@app.route('/tomar-reserva/<int:reserva_id>', methods=['POST'])
def tomar_reserva(reserva_id):
    groups, user_id, error = decode_jwt_token()

    if error:
        return error, 401
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if 'Empleado' not in groups:
        return 'No autorizado: Necesitas ser Empleado', 403
    # Aquí procesas la solicitud para tomar la reserva
    # Por ejemplo, puedes actualizar el estado de la reserva en la base de datos
    
    return jsonify({'message': 'Reserva tomada con éxito'}), 200


if __name__ == '__main__':
    app.secret_key = os.environ.get('JWT_SECRET_KEY')  # Cambia esta clave por una segura
    app.run(host='0.0.0.0', port=5000, debug=True)
