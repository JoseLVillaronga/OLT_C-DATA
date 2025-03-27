# Limpiador de ONTs para OLT GPON

Este script automatiza el proceso de limpieza de ONTs en una OLT GPON C-Data, permitiendo eliminar todas las ONTs de puertos específicos de manera programada.

## Descripción

Este proyecto implementa una solución automatizada para la gestión de ONTs (Optical Network Terminals) en una OLT GPON C-Data. El script está diseñado para:

- Eliminar automáticamente todas las ONTs de puertos GPON específicos
- Ejecutarse de manera programada sin intervención manual
- Mantener un registro detallado de todas las operaciones realizadas
- Almacenar el historial de operaciones en una base de datos MongoDB

La herramienta es especialmente útil en entornos donde se requiere:
- Limpieza periódica de ONTs en puertos GPON
- Mantenimiento automatizado de la red
- Seguimiento y registro de operaciones de mantenimiento
- Gestión remota de dispositivos GPON

El script está diseñado para ejecutarse cada 4 horas por defecto, pero puede ser configurado según las necesidades específicas del entorno.

## Características

- Eliminación automática de ONTs en puertos GPON especificados
- Soporte para procesar rangos de puertos o puertos individuales
- Registro detallado de operaciones en archivo de log
- Almacenamiento de resultados en MongoDB
- Ejecución programada mediante crontab
- Manejo seguro de credenciales mediante variables de entorno

## Requisitos

- Python 3.12 o superior
- MongoDB
- Acceso SSH a la OLT
- Credenciales de administrador de la OLT

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd OLT_C-DATA
```

2. Crear y activar el entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
.\venv\Scripts\activate  # En Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
```env
#Datos SSH del OLT C-Data
SSH_USER=root
SSH_PASSWORD=admin
SSH_HOST=192.168.111.100

#Datos MongoDB local
MONGO_USERNAME=Admin
MONGO_PASSWORD=sloch1618
MONGO_HOST=localhost
MONGO_PORT=27017
```

## Uso

### Ejecución básica
```bash
python olt_ont_cleaner.py
```
Por defecto, procesará los puertos 1-4.

### Especificar puertos
```bash
# Procesar un rango de puertos
python olt_ont_cleaner.py --ports 1-6

# Procesar un puerto específico
python olt_ont_cleaner.py --ports 3
```

### Ver ayuda
```bash
python olt_ont_cleaner.py --help
```

## Programación con crontab

Para ejecutar el script cada 4 horas, agregar la siguiente línea al crontab:
```bash
0 */4 * * * cd /ruta/al/proyecto && /ruta/al/venv/bin/python olt_ont_cleaner.py >> /ruta/al/proyecto/cron.log 2>&1
```

## Estructura de logs

Los logs se guardan en dos lugares:
1. Archivo `olt_ont_cleaner.log`: Contiene el registro detallado de todas las operaciones
2. MongoDB: Almacena los resultados de cada operación de eliminación

### Formato de logs
```
2024-03-27 18:11:00 - INFO - ==================================================
2024-03-27 18:11:00 - INFO - INICIANDO PROCESO DE LIMPIEZA DE ONTs
2024-03-27 18:11:00 - INFO - Fecha y hora: 2024-03-27 18:11:00 UTC
2024-03-27 18:11:00 - INFO - Puertos a procesar: [1, 2, 3, 4]
2024-03-27 18:11:00 - INFO - ==================================================
```

## Estructura de datos en MongoDB

Colección: `ont_deletions`

Documento:
```json
{
    "timestamp": ISODate("2024-03-27T18:11:00Z"),
    "port": 1,
    "onts_deleted": 103,
    "status": "success"
}
```

## Resumen de operación

Al finalizar cada ejecución, el script muestra un resumen con:
- Total de ONTs eliminadas
- Desglose por puerto
- Estado de la operación

## Consideraciones de seguridad

- Las credenciales se manejan mediante variables de entorno
- No se almacenan contraseñas en el código
- Se recomienda restringir los permisos del archivo `.env`
- Los logs contienen información sensible, asegurar su protección

## Solución de problemas

1. **Error de conexión SSH**:
   - Verificar que la OLT esté accesible
   - Comprobar credenciales en el archivo `.env`
   - Verificar que el puerto SSH (22) esté abierto

2. **Error de conexión MongoDB**:
   - Verificar que MongoDB esté corriendo
   - Comprobar credenciales en el archivo `.env`
   - Verificar que el puerto MongoDB (27017) esté accesible

3. **Error en la ejecución de comandos**:
   - Verificar los logs para detalles específicos
   - Comprobar que los puertos especificados existan
   - Verificar que se tenga permisos suficientes en la OLT

## Contribuciones

Las contribuciones son bienvenidas. Por favor, seguir estos pasos:
1. Fork el repositorio
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Crear un Pull Request

## Licencia

[Especificar la licencia del proyecto] 