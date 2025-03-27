from flask import Flask, render_template, request, session, Markup
from flask_paginate import Pagination, get_page_parameter
from pymongo import MongoClient
from datetime import datetime
import os
import pytz
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de MongoDB
client = MongoClient(
    host=os.getenv('MONGO_HOST'),
    port=int(os.getenv('MONGO_PORT')),
    username=os.getenv('MONGO_USERNAME'),
    password=os.getenv('MONGO_PASSWORD')
)
db = client['olt_operations']
collection = db['ont_deletions']

# Configuración de la aplicación
app.config['ITEMS_PER_PAGE'] = 10  # Reducido a 10 para ver mejor la paginación
app.config['SECRET_KEY'] = os.urandom(24)

# Lista de zonas horarias comunes en español
ZONAS_HORARIAS = [
    ('UTC', 'UTC'),
    ('America/Argentina/Buenos_Aires', 'Argentina'),
    ('America/Santiago', 'Chile'),
    ('America/Bogota', 'Colombia'),
    ('America/Mexico_City', 'México'),
    ('America/Lima', 'Perú'),
    ('America/Caracas', 'Venezuela'),
    ('Europe/Madrid', 'España'),
]

def format_datetime(dt, timezone_name):
    """Formatea la fecha según la zona horaria seleccionada"""
    if timezone_name and timezone_name != 'UTC':
        timezone = pytz.timezone(timezone_name)
        dt = dt.replace(tzinfo=pytz.UTC)
        dt = dt.astimezone(timezone)
    return dt.strftime('%Y-%m-%d %H:%M:%S %Z')

@app.route('/', methods=['GET'])
def index():
    # Obtener zona horaria seleccionada
    timezone_name = request.args.get('timezone', 'UTC')
    
    # Obtener el número de página actual
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = app.config['ITEMS_PER_PAGE']
    offset = (page - 1) * per_page
    
    # Obtener total de registros
    total = collection.count_documents({})
    
    # Obtener registros paginados
    records = list(collection.find()
                  .sort('timestamp', -1)
                  .skip(offset)
                  .limit(per_page))
    
    # Formatear fechas según la zona horaria seleccionada
    for record in records:
        record['timestamp'] = format_datetime(record['timestamp'], timezone_name)
    
    # Crear objeto de paginación
    pagination = Pagination(
        page=page,
        total=total,
        per_page=per_page,
        css_framework='bootstrap5',
        display_msg='Mostrando registros <b>{start}</b> a <b>{end}</b> de <b>{total}</b>',
        record_name='registros',
        alignment='center',
        show_single_page=True,
        prev_label='Anterior',
        next_label='Siguiente',
        format_total=True,
        format_number=True
    )
    
    return render_template('index.html', 
                         records=records, 
                         pagination=pagination,
                         total=total,
                         timezone=timezone_name,
                         zonas_horarias=ZONAS_HORARIAS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5717, debug=True) 