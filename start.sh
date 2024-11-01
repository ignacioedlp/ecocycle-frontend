#!/bin/sh

# Ejecuta las migraciones
flask db upgrade

# Inicia la aplicación
exec python app.py
