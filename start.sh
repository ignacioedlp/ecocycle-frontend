#!/bin/sh

# Ejecuta las migraciones
flask db upgrade

# Seed
# python -c 'from app import app; from seed import run_seed; with app.app_context(): run_seed()'

# Inicia la aplicación
exec python app.py
