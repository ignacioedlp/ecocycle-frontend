from flask import Flask, session
from flask_migrate import Migrate
from database import db  
import sys
import os
from api.routes import api
from ui.routes import ui

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')  # Cambia esta clave por una segura
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
JWT_SECRET_KEY  = os.environ.get('JWT_SECRET_KEY')   # Cambia esta clave por una segura
API_URL = os.environ.get('API_URL')
db.init_app(app)
migrate = Migrate(app, db)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# API Section
app.register_blueprint(ui)
app.register_blueprint(api)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.secret_key = os.environ.get('JWT_SECRET_KEY')  # Cambia esta clave por una segura
    app.run(host='0.0.0.0', port=5000, debug=True)
