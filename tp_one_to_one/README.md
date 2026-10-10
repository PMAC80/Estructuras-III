# TP: Python Back End One to One

Este proyecto implementa una API REST en Python utilizando Flask, Connexion y SQLAlchemy, demostrando una relación de base de datos **Uno a Uno (1:1)** entre una `Person` y su `PersonDetail`.

## Cómo ejecutar
1. Activar entorno virtual: `.\venv\Scripts\activate`
2. Instalar dependencias: `pip install -r requirements.txt`
3. Crear la base de datos: `python build_database.py`
4. Iniciar el servidor: `python app.py`
5. Visitar: http://localhost:8000 (Vista web) o http://localhost:8000/api/ui (Documentación Swagger).