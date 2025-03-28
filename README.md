# Limpiador de ONTs para OLT GPON

Este script automatiza el proceso de limpieza de ONTs en una OLT GPON C-Data, permitiendo eliminar todas las ONTs de puertos específicos de manera programada.

## Descripción

Este proyecto implementa una solución automatizada para la gestión de ONTs (Optical Network Terminals) en una OLT GPON C-Data. El script está diseñado para:

- Eliminar automáticamente todas las ONTs de puertos GPON específicos
- Eliminar selectivamente solo ONTs offline (desconectadas) de puertos específicos
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
- Modo offline para eliminar solo ONTs desconectadas
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
SSH_USER=user
SSH_PASSWORD=password
SSH_HOST=192.168.1.100

#Datos MongoDB local
MONGO_USERNAME=user
MONGO_PASSWORD=pasword
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

### Modo offline (solo ONTs desconectadas)
```bash
# Eliminar solo ONTs offline en todos los puertos predeterminados (1-4)
python olt_ont_cleaner.py --offline

# Eliminar solo ONTs offline en un rango específico de puertos
python olt_ont_cleaner.py --ports 1-6 --offline

# Eliminar solo ONTs offline en un puerto específico
python olt_ont_cleaner.py --ports 3 --offline
```

En el modo offline:
- Solo se eliminan ONTs que están desconectadas
- No se guardan registros en MongoDB
- El comando ejecutado es `ont delete {puerto} offline-list all` en lugar de `ont delete {puerto} all`

> **IMPORTANTE**: Las operaciones ejecutadas en modo offline **NO aparecerán en la interfaz web**, ya que no se almacenan en MongoDB. Esta es una característica diseñada intencionalmente para mantener la interfaz web limpia y mostrar solo las operaciones completas de limpieza. Si necesita verificar las acciones realizadas en modo offline, consulte los archivos de log (olt_ont_cleaner.log o cron_offline.log).

### Ver ayuda
```bash
python olt_ont_cleaner.py --help
```

## Programación con crontab

### Ejemplo de ejecución cada 4 horas (6 AM a 8 PM)
Para ejecutar el script cada 4 horas entre las 6:00 y las 20:00 (8 PM), agregar la siguiente línea al crontab:

```bash
0 6,10,14,18 * * * cd /home/jose/OLT_C-DATA && /home/jose/OLT_C-DATA/venv/bin/python olt_ont_cleaner.py >> /home/jose/OLT_C-DATA/cron.log 2>&1
```

Desglose de la configuración:
- `0` - Minuto 0 de cada hora
- `6,10,14,18` - Se ejecutará a las 6:00, 10:00, 14:00 y 18:00
- `* * *` - Todos los días, todos los meses, todos los días de la semana
- `cd /home/jose/OLT_C-DATA` - Se posiciona en el directorio del proyecto
- `/home/jose/OLT_C-DATA/venv/bin/python` - Usa el Python del entorno virtual
- `>> /home/jose/OLT_C-DATA/cron.log 2>&1` - Guarda tanto la salida estándar como los errores en el archivo cron.log

### Ejemplo de ejecución del modo offline cada 5 minutos durante horario laboral
Para eliminar ONTs desconectadas de manera más frecuente durante el día, se puede configurar una tarea adicional que ejecute el script en modo offline cada 5 minutos entre las 6:00 y las 18:00:

```bash
*/5 6-18 * * * cd /home/jose/OLT_C-DATA && /home/jose/OLT_C-DATA/venv/bin/python olt_ont_cleaner.py --offline >> /home/jose/OLT_C-DATA/cron_offline.log 2>&1
```

Desglose de la configuración:
- `*/5` - Cada 5 minutos
- `6-18` - Entre las 6:00 AM y las 6:00 PM
- `* * *` - Todos los días, todos los meses, todos los días de la semana
- `--offline` - Ejecuta el script en modo offline (solo elimina ONTs desconectadas)
- `cron_offline.log` - Guarda los logs en un archivo separado para facilitar su análisis

Esta configuración complementa la tarea principal, permitiendo mantener la red más limpia de manera proactiva al eliminar constantemente dispositivos que se desconectan, sin afectar a los que están operativos.

Para agregar estas líneas al crontab:
```bash
crontab -e
```

## Estructura de logs

Los logs se guardan en dos lugares:
1. Archivo `olt_ont_cleaner.log`: Contiene el registro detallado de todas las operaciones
2. MongoDB: Almacena los resultados de cada operación de eliminación (excepto en modo offline)

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

Nota: En modo offline (con parámetro `--offline`), no se guardan registros en MongoDB.

### Visualización en la interfaz web

La interfaz web (app.py) muestra únicamente los registros almacenados en MongoDB. Esto significa que:

- Todas las operaciones estándar (sin `--offline`) son visibles en la interfaz web
- Las operaciones realizadas con el parámetro `--offline` NO aparecen en la interfaz web
- Si se configuran tareas programadas que ejecutan el script en modo offline (por ejemplo, cada 5 minutos), estas ejecuciones no serán visibles en la interfaz

Esta separación es intencional para mantener la interfaz limpia y enfocada en las operaciones completas de limpieza, mientras que las operaciones de mantenimiento continuo en modo offline se registran solo en los archivos de log.

## Resumen de operación

Al finalizar cada ejecución, el script muestra un resumen con:
- Total de ONTs eliminadas
- Desglose por puerto
- Estado de la operación
- Indicación de si se ejecutó en modo offline

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

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

La Licencia MIT es una licencia de software permisiva que permite:
- Uso comercial
- Modificación
- Distribución
- Uso privado

Sin ninguna garantía y con la única obligación de mantener el aviso de copyright y la licencia. 
