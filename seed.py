from app import app, db
from models.models import Material, DepositoComunal, PuntoDeRecoleccion  # Importa tu modelo

def seed_materials():
    # Definir los materiales a insertar
    materiales_a_insertar = [
        Material(name="Madera", hide=False, precio=100),
        Material(name="Metal", hide=False, precio=100),
        Material(name="Carton", hide=False, precio=100),
        Material(name="Plastico", hide=False, precio=100),
        Material(name="Cobre", hide=False, precio=100)
    ]
    
    # Verificar si el material ya existe antes de insertarlo
    for material in materiales_a_insertar:
        if not Material.query.filter_by(name=material.name).first():
            db.session.add(material)
    
    db.session.commit()
    print("Seed materials inserted successfully.")

def seed_puntos_de_recoleccion():
    # Definir los puntos de recolección a insertar
    puntos_a_insertar = [
        PuntoDeRecoleccion(name="Almacen 21", hide=False),
        PuntoDeRecoleccion(name="Reciclados 23", hide=False),
        PuntoDeRecoleccion(name="Almacen 23", hide=False),
        PuntoDeRecoleccion(name="Productos 2", hide=False),
        PuntoDeRecoleccion(name="Punto 5", hide=False)
    ]
    
    # Verificar si el punto de recolección ya existe antes de insertarlo
    for punto in puntos_a_insertar:
        if not PuntoDeRecoleccion.query.filter_by(name=punto.name).first():
            db.session.add(punto)
    
    db.session.commit()
    print("Seed puntos de recoleccion inserted successfully.")

def seed_depositos():
    # Definir los depósitos a insertar
    depositos_a_insertar = [
        DepositoComunal(name="Depósito 23 y 21", hide=False),
        DepositoComunal(name="Depósito 21 y 6", hide=False),
        DepositoComunal(name="Depósito 21 y 30", hide=False),
        DepositoComunal(name="Depósito 33 y 2", hide=False),
        DepositoComunal(name="Depósito 1 y 60", hide=False)
    ]
    
    # Verificar si el depósito ya existe antes de insertarlo
    for deposito in depositos_a_insertar:
        if not DepositoComunal.query.filter_by(name=deposito.name).first():
            db.session.add(deposito)
    
    db.session.commit()
    print("Seed depositos inserted successfully.")

with app.app_context():
    seed_materials()
    seed_puntos_de_recoleccion()
    seed_depositos()