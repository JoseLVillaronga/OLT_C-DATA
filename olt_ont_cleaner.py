#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import argparse
from datetime import datetime, UTC
from dotenv import load_dotenv
from netmiko import ConnectHandler
from pymongo import MongoClient
from dateutil import parser

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('olt_ont_cleaner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_port_range(port_range):
    """Parsea el rango de puertos especificado"""
    try:
        if '-' in port_range:
            start, end = map(int, port_range.split('-'))
            return list(range(start, end + 1))
        else:
            return [int(port_range)]
    except ValueError:
        logger.error(f"Formato de puertos inválido: {port_range}")
        sys.exit(1)

def get_ports_to_process(args):
    """Determina qué puertos procesar basado en los argumentos"""
    if args.ports:
        return parse_port_range(args.ports)
    return list(range(1, 5))  # Por defecto, puertos 1-4

def connect_to_mongodb():
    """Establece conexión con MongoDB"""
    try:
        client = MongoClient(
            host=os.getenv('MONGO_HOST'),
            port=int(os.getenv('MONGO_PORT')),
            username=os.getenv('MONGO_USERNAME'),
            password=os.getenv('MONGO_PASSWORD')
        )
        db = client['olt_operations']
        return db
    except Exception as e:
        logger.error(f"Error al conectar con MongoDB: {str(e)}")
        raise

def connect_to_olt():
    """Establece conexión con la OLT"""
    try:
        device = {
            'device_type': 'generic',
            'host': os.getenv('SSH_HOST'),
            'username': os.getenv('SSH_USER'),
            'password': os.getenv('SSH_PASSWORD'),
            'port': 22,
            'verbose': True,
            'global_delay_factor': 4,
            'session_timeout': 60,
            'auth_timeout': 60,
            'banner_timeout': 20,
            'read_timeout_override': 30,
            'fast_cli': False,
        }
        return ConnectHandler(**device)
    except Exception as e:
        logger.error(f"Error al conectar con la OLT: {str(e)}")
        raise

def execute_olt_commands(connection, ports):
    """Ejecuta los comandos en la OLT"""
    try:
        total_onts_deleted = 0
        port_results = {}
        
        # Esperar a que aparezca el prompt inicial
        logger.info("Esperando prompt inicial...")
        output = connection.send_command('\n', expect_string=r'OLT>')
        logger.debug(f"Prompt inicial: {output}")
        
        # Comando enable
        logger.info("Ejecutando comando: enable")
        output = connection.send_command('enable', expect_string=r'OLT#')
        logger.debug(f"Salida del comando enable: {output}")
        
        # Comando config
        logger.info("Ejecutando comando: config")
        output = connection.send_command('config', expect_string=r'OLT\(config\)#')
        logger.debug(f"Salida del comando config: {output}")
        
        # Comando interface gpon
        logger.info("Ejecutando comando: interface gpon 0/0")
        output = connection.send_command('interface gpon 0/0', expect_string=r'OLT\(config-interface-gpon-0\/0\)#')
        logger.debug(f"Salida del comando interface: {output}")

        # Eliminar ONTs en los puertos especificados
        for port in ports:
            cmd = f'ont delete {port} all'
            logger.info(f"Ejecutando comando: {cmd}")
            output = connection.send_command(cmd, expect_string=r'\(y/n\):')
            logger.debug(f"Salida del comando {cmd}: {output}")
            
            # Enviar confirmación 'y'
            output = connection.send_command('y', expect_string=r'OLT\(config-interface-gpon-0\/0\)#')
            logger.debug(f"Salida de la confirmación: {output}")
            
            # Procesar la salida para obtener el número de ONTs eliminadas
            if 'success:' in output:
                success_count = int(output.split('success:')[1].strip())
                logger.info(f"ONTs eliminadas en puerto {port}: {success_count}")
                total_onts_deleted += success_count
                port_results[port] = success_count
                
                # Guardar en MongoDB
                save_to_mongodb(port, success_count)
        
        # Imprimir resumen final
        logger.info("=" * 50)
        logger.info("RESUMEN DE OPERACIÓN")
        logger.info("=" * 50)
        logger.info(f"Total de ONTs eliminadas: {total_onts_deleted}")
        logger.info("Desglose por puerto:")
        for port, count in port_results.items():
            logger.info(f"  Puerto {port}: {count} ONTs")
        logger.info("=" * 50)
        
        return total_onts_deleted, port_results

    except Exception as e:
        logger.error(f"Error al ejecutar comandos en la OLT: {str(e)}")
        raise

def save_to_mongodb(port, ont_count):
    """Guarda los resultados en MongoDB"""
    try:
        db = connect_to_mongodb()
        collection = db['ont_deletions']
        
        document = {
            'timestamp': datetime.now(UTC),
            'port': port,
            'onts_deleted': ont_count,
            'status': 'success'
        }
        
        collection.insert_one(document)
        logger.info(f"Datos guardados en MongoDB para puerto {port}")
    except Exception as e:
        logger.error(f"Error al guardar en MongoDB: {str(e)}")
        raise

def main():
    """Función principal"""
    try:
        # Configurar el parser de argumentos
        parser = argparse.ArgumentParser(description='Script para limpiar ONTs en puertos GPON')
        parser.add_argument('--ports', 
                          help='Rango de puertos a procesar (ej: 1-6 o 3)',
                          default=None)
        args = parser.parse_args()

        # Cargar variables de entorno
        load_dotenv()
        
        # Determinar qué puertos procesar
        ports_to_process = get_ports_to_process(args)
        
        logger.info("=" * 50)
        logger.info("INICIANDO PROCESO DE LIMPIEZA DE ONTs")
        logger.info(f"Fecha y hora: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info(f"Puertos a procesar: {ports_to_process}")
        logger.info("=" * 50)
        
        # Conectar a la OLT
        connection = connect_to_olt()
        
        # Ejecutar comandos
        total_onts, port_results = execute_olt_commands(connection, ports_to_process)
        
        # Cerrar conexión
        connection.disconnect()
        
        logger.info("=" * 50)
        logger.info("PROCESO COMPLETADO EXITOSAMENTE")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Error en el proceso principal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 