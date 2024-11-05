#!/bin/sh

# Ejecuta las migraciones
flask db upgrade

# Seed
python seed.py

# Inicia la aplicación
exec python app.py
