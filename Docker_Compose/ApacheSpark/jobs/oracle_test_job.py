#!/usr/bin/env python3
"""
Ejemplo de trabajo de Spark con Oracle Database
"""

import cx_Oracle
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import sys
import os

def create_spark_session():
    """Crear una sesión de Spark con soporte para Oracle"""
    return SparkSession.builder \
        .appName("Spark Oracle Job") \
        .master("spark://spark-master:7077") \
        .config("spark.jars", "/opt/spark/jars/ojdbc8.jar") \
        .config("spark.driver.extraClassPath", "/opt/spark/jars/ojdbc8.jar") \
        .config("spark.executor.extraClassPath", "/opt/spark/jars/ojdbc8.jar") \
        .getOrCreate()

def test_cx_oracle_connection():
    """Probar conexión directa con cx_Oracle"""
    try:
        print("Probando cx_Oracle...")
        print(f"cx_Oracle version: {cx_Oracle.version}")
        print(f"Oracle Client version: {cx_Oracle.clientversion()}")
        print("cx_Oracle está funcionando correctamente!")
        return True
    except Exception as e:
        print(f"Error con cx_Oracle: {e}")
        return False

def create_oracle_config():
    """Configuración de Oracle (usar variables de entorno en producción)"""
    return {
        "host": os.getenv("ORACLE_HOST", "localhost"),
        "port": os.getenv("ORACLE_PORT", "1521"),
        "service_name": os.getenv("ORACLE_SERVICE", "ORCL"),
        "username": os.getenv("ORACLE_USER", "your_username"),
        "password": os.getenv("ORACLE_PASSWORD", "your_password")
    }

def test_oracle_connection_direct(oracle_config):
    """Probar conexión directa a Oracle"""
    try:
        print("Probando conexión directa a Oracle...")
        
        dsn = cx_Oracle.makedsn(
            oracle_config['host'], 
            oracle_config['port'], 
            service_name=oracle_config['service_name']
        )
        
        connection = cx_Oracle.connect(
            user=oracle_config['username'],
            password=oracle_config['password'],
            dsn=dsn
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT SYSDATE, USER FROM DUAL")
        result = cursor.fetchone()
        print(f"Conexión exitosa! Fecha: {result[0]}, Usuario: {result[1]}")
        
        cursor.close()
        connection.close()
        return True
        
    except cx_Oracle.Error as error:
        print(f"Error de conexión Oracle: {error}")
        return False
    except Exception as e:
        print(f"Error general: {e}")
        return False

def test_spark_oracle_connection(spark, oracle_config):
    """Probar conexión de Spark a Oracle"""
    try:
        print("Probando conexión Spark-Oracle...")
        
        oracle_url = f"jdbc:oracle:thin:@{oracle_config['host']}:{oracle_config['port']}:{oracle_config['service_name']}"
        
        # Leer datos de prueba desde Oracle
        df = spark.read \
            .format("jdbc") \
            .option("url", oracle_url) \
            .option("dbtable", "(SELECT SYSDATE as CURRENT_DATE, USER as CURRENT_USER, 'Test' as MESSAGE FROM DUAL)") \
            .option("user", oracle_config['username']) \
            .option("password", oracle_config['password']) \
            .option("driver", "oracle.jdbc.driver.OracleDriver") \
            .load()
        
        print("Datos leídos desde Oracle con Spark:")
        df.show()
        return True
        
    except Exception as e:
        print(f"Error en conexión Spark-Oracle: {e}")
        return False

def create_sample_data_and_write_to_oracle(spark, oracle_config):
    """Crear datos de muestra y escribir a Oracle"""
    try:
        print("Creando datos de muestra...")
        
        # Crear DataFrame de ejemplo
        from datetime import datetime
        
        data = [
            (1, "Usuario1", 25, datetime.now()),
            (2, "Usuario2", 30, datetime.now()),
            (3, "Usuario3", 35, datetime.now()),
            (4, "Usuario4", 28, datetime.now())
        ]
        
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("nombre", StringType(), True),
            StructField("edad", IntegerType(), True),
            StructField("fecha_creacion", TimestampType(), True)
        ])
        
        df = spark.createDataFrame(data, schema)
        print("DataFrame de muestra creado:")
        df.show()
        
        # Escribir a Oracle
        oracle_url = f"jdbc:oracle:thin:@{oracle_config['host']}:{oracle_config['port']}:{oracle_config['service_name']}"
        
        df.write \
            .format("jdbc") \
            .option("url", oracle_url) \
            .option("dbtable", "SPARK_TEST_TABLE") \
            .option("user", oracle_config['username']) \
            .option("password", oracle_config['password']) \
            .option("driver", "oracle.jdbc.driver.OracleDriver") \
            .mode("overwrite") \
            .save()
        
        print("Datos escritos exitosamente a Oracle!")
        return True
        
    except Exception as e:
        print(f"Error al escribir a Oracle: {e}")
        return False

def main():
    """Función principal"""
    print("=== Iniciando pruebas de Oracle con Spark ===")
    
    # Probar cx_Oracle
    if not test_cx_oracle_connection():
        print("Error: cx_Oracle no está funcionando correctamente")
        return False
    
    # Configuración de Oracle
    oracle_config = create_oracle_config()
    print(f"Configuración Oracle: {oracle_config['host']}:{oracle_config['port']}/{oracle_config['service_name']}")
    
    # Crear sesión Spark
    spark = create_spark_session()
    
    try:
        print(f"Spark iniciado correctamente. Versión: {spark.version}")
        
        # Probar conexión directa (comentar si no tienes Oracle disponible)
        # test_oracle_connection_direct(oracle_config)
        
        # Probar conexión Spark-Oracle (comentar si no tienes Oracle disponible)
        # test_spark_oracle_connection(spark, oracle_config)
        
        # Crear y escribir datos de muestra (comentar si no tienes Oracle disponible)
        # create_sample_data_and_write_to_oracle(spark, oracle_config)
        
        print("=== Todas las pruebas completadas ===")
        return True
        
    except Exception as e:
        print(f"Error durante las pruebas: {e}")
        return False
    
    finally:
        spark.stop()
        print("Sesión Spark finalizada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)