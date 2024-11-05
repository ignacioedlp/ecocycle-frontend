from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from marshmallow import validate
from database import db

class DepositoComunal(db.Model):
    __tablename__ = 'depositos_comunales' 

    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(100), nullable=False)  
    hide = db.Column(db.Boolean, default=False) 

    def __repr__(self):
        return f'<DepositoComunal {self.name}>'

class Recoleccion(db.Model):
    __tablename__ = 'recolecciones' 
    id = db.Column(db.Integer, primary_key=True)

    # Atributos de la tabla Orden
    PENDIENTE = 'Pendiente'
    PROCESADO = 'Procesado'
    CANCELADO = 'Cancelado'

    STATUS_CHOICES = [
        (PENDIENTE, 'Pendiente'),
        (PROCESADO, 'Procesado'),
        (CANCELADO, 'Cancelado'),
    ]

    estado = db.Column(db.String(10), default=PENDIENTE)  

    recolector = db.Column(db.String(80), nullable=True)
    empleado = db.Column(db.String(80), nullable=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materiales.id'), nullable=False)
    case_bonita_id = db.Column(db.String(100), nullable=True)
    deposito_id = db.Column(db.Integer, db.ForeignKey('depositos_comunales.id'), nullable=False)  # Corregido el nombre de la tabla
    cantidad_inicial = db.Column(Numeric(10, 2), nullable=False)  
    punto_de_recoleccion_id = db.Column(db.Integer, db.ForeignKey('puntos_de_recoleccion.id'), nullable=False)  # Corregido el nombre de la tabla
    cantidad_final = db.Column(Numeric(10, 2), nullable=True)  
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)  
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)  

    # Relaciones
    material = db.relationship('Material', backref='recolecciones')
    deposito = db.relationship('DepositoComunal', backref='recolecciones')
    punto_recoleccion = db.relationship('PuntoDeRecoleccion', backref='recolecciones')

class PuntoDeRecoleccion(db.Model):
    __tablename__ = 'puntos_de_recoleccion' 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    hide = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=True)
    raffles = db.relationship('Raffle', backref='punto_de_recoleccion', lazy=True)
    created_at = db.Column(db.DateTime, default=db.func.now())  
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())  

class Material(db.Model):
    __tablename__ = 'materiales' 

    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(100), nullable=False) 
    hide = db.Column(db.Boolean, default=False)  
    precio = db.Column(Numeric(10, 2), nullable=True)
    
    def __repr__(self):
        return f'<Material {self.name}>'

class Stock(db.Model):
    __tablename__ = 'stocks' 

    id = db.Column(db.Integer, primary_key=True)
    deposito_id = db.Column(db.Integer, db.ForeignKey('depositos_comunales.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materiales.id'), nullable=False)
    stock = db.Column(Numeric(10, 2), nullable=False)

class Raffle(db.Model):
    __tablename__ = 'raffles'

    id = db.Column(db.Integer, primary_key=True)
    punto_de_recoleccion_id = db.Column(db.Integer, db.ForeignKey('puntos_de_recoleccion.id'), nullable=False)  # Corregido el nombre de la tabla
    token = db.Column(db.String(100), unique=True, nullable=False)
    month = db.Column(db.String(7), nullable=False)  # Formato 'YYYY-MM'
    created_at = db.Column(db.DateTime, default=db.func.now())  
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())  