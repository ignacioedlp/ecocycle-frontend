import json
from flask import Blueprint, request, jsonify
from helpers.completar_reserva import completar_reserva_bonita
from helpers.get_reservas import get_reservas
from helpers.tomar_reserva import tomar_reserva_bonita
from models.models import PuntoDeRecoleccion, Raffle, Recoleccion, db, Stock
from ui.routes import get_user_info
import uuid
import datetime

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/recolecciones', methods=['POST'])
def api_create_recoleccion():
    data = json.loads(request.data)  # Convertir los datos de bytes a un diccionario
    material_id = data['material_id']
    deposito_id = data['deposito_id']
    cantidad = data['cantidad']
    case_bonita_id = data['case_bonita_id']
    punto_de_recoleccion_id = data['punto_de_recoleccion_id']
    recolector_username = data['recolector_username']

    recoleccion = Recoleccion(material_id=material_id, deposito_id=deposito_id, cantidad_inicial=cantidad, case_bonita_id=case_bonita_id, punto_de_recoleccion_id=punto_de_recoleccion_id, recolector=recolector_username)
    db.session.add(recoleccion)
    db.session.commit()
    return jsonify({'id': recoleccion.id}), 200

@api.route('/completar-recoleccion/<int:recoleccion_id>', methods=['PUT'])
def api_finalizar_recoleccion(recoleccion_id):
    data = json.loads(request.data)  # Convertir los datos de bytes a un diccionario
    cantidad_final = data['cantidad_final']
    recoleccion = Recoleccion.query.get(recoleccion_id)
    recoleccion.cantidad_final = cantidad_final
    recoleccion.empleado = data['empleado_username']
    recoleccion.estado = recoleccion.PROCESADO

    stock = Stock.query.filter_by(material_id=recoleccion.material_id, deposito_id=recoleccion.deposito_id).first()
    if stock:
        stock.stock += int(cantidad_final)
    else:
        stock = Stock(material_id=recoleccion.material_id, deposito_id=recoleccion.deposito_id, stock=int(cantidad_final))
        db.session.add(stock)

    db.session.commit()
    return jsonify({'id': recoleccion.id}), 200

@api.route('/tomar-reserva/<int:reserva_id>', methods=['POST'])
def tomar_reserva(reserva_id):
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return 'No autorizado: Necesitas ser Empleado', 403
    # Aquí procesas la solicitud para tomar la reserva
    # Por ejemplo, puedes actualizar el estado de la reserva en la base de datos
    data = request.form  # Convertir los datos de bytes a un diccionario
    deposito_id = data['deposito_id']

    tomar_reserva_bonita(reserva_id, deposito_id)
    
    return jsonify({'message': 'Reserva tomada con éxito'}), 200


@api.route('/completar-reserva/<int:reserva_id>', methods=['POST'])
def completar_reserva(reserva_id):
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return 'No autorizado: Necesitas ser Empleado', 403

    data = json.loads(request.data)  # Convertir los datos de bytes a un diccionario
    material_id = data['material_id']
    deposito_id = data['deposito_id']
    cantidad = data['cantidad']

    # Verificar si hay stock suficiente del material en el depósito especificado
    stock = Stock.query.filter_by(material_id=material_id, deposito_id=deposito_id).first()
    if stock:
        if stock.stock >= int(float(cantidad)):
            stock.stock -= int(float(cantidad))
            db.session.commit()
        else:
            return jsonify({'message': 'No hay stock suficiente'}), 400
    else:
        return jsonify({'message': 'No hay stock disponible'}), 400

    completar_reserva_bonita(reserva_id)

    
    return jsonify({'message': 'Reserva completada con éxito'}), 200

@api.route('/consultar-reservas', methods=['GET'])
def consultar_reservas():
    user_id, user_name, role_name = get_user_info()
    
    # Verificar si el usuario tiene el grupo 'Empleado'
    if role_name != 'Empleado':
        return 'No autorizado: Necesitas ser Empleado', 403
    
    material_id = request.args.get('material_id')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    return get_reservas(fecha_inicio, fecha_fin, material_id)

@api.route('/sorteo', methods=['POST'])
def generar_token_sorteo():
    data = request.get_json()
    punto_de_recoleccion_id = int(data.get('punto_de_recoleccion_id'))

    if not punto_de_recoleccion_id:
        return jsonify({'error': 'Punto de recolección es requerido'}), 400

    # Verificar si el punto de recolección existe
    punto = PuntoDeRecoleccion.query.get(punto_de_recoleccion_id)
    if not punto:
        return jsonify({'error': 'Punto de recolección no encontrado'}), 404

    # Generar el mes actual en formato 'YYYY-MM'
    mes_actual = datetime.datetime.utcnow().strftime('%Y-%m')

    # Verificar si ya existe un token para este mes y este punto de recolección
    sorteo_existente = Raffle.query.filter_by(
        punto_de_recoleccion_id=punto_de_recoleccion_id,
        month=mes_actual
    ).first()

    if sorteo_existente:
        return jsonify({'token': sorteo_existente.token}), 200

    # Generar un nuevo token
    nuevo_token = str(uuid.uuid4())

    # Crear una nueva entrada de sorteo
    nuevo_sorteo = Raffle(
        punto_de_recoleccion_id=punto_de_recoleccion_id,
        token=nuevo_token,
        month=mes_actual
    )

    db.session.add(nuevo_sorteo)
    db.session.commit()

    return jsonify({'id': nuevo_sorteo.id}), 201