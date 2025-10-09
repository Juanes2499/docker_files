#!/usr/bin/env python3
"""
Ejemplo de trabajo de Spark para procesar datos
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import count, avg, max, min
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import sys

def create_spark_session():
    """Crear una sesión de Spark"""
    return SparkSession.builder \
        .appName("Spark Job Example") \
        .master("spark://spark-master:7077") \
        .getOrCreate()

def process_data(spark):
    """Procesar datos de ejemplo"""
    # Crear datos de ejemplo
    data = []
    for i in range(1000):
        data.append((f"user_{i}", i % 10, (i * 2) % 100))
    
    schema = StructType([
        StructField("user_id", StringType(), True),
        StructField("category", IntegerType(), True),
        StructField("value", IntegerType(), True)
    ])
    
    df = spark.createDataFrame(data, schema)
    
    # Realizar transformaciones
    result = df.groupBy("category") \
        .agg(
            count("user_id").alias("user_count"),
            avg("value").alias("avg_value"),
            max("value").alias("max_value"),
            min("value").alias("min_value")
        ) \
        .orderBy("category")
    
    return result

def main():
    """Función principal"""
    spark = create_spark_session()
    
    try:
        print("Iniciando procesamiento de datos...")
        
        # Procesar datos
        result_df = process_data(spark)
        
        # Mostrar resultados
        print("Resultados del procesamiento:")
        result_df.show()
        
        # Guardar resultados
        output_path = "/opt/spark/data/job_results"
        result_df.write.mode("overwrite").parquet(output_path)
        print(f"Resultados guardados en: {output_path}")
        
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
        sys.exit(1)
    
    finally:
        spark.stop()
        print("Trabajo completado")

if __name__ == "__main__":
    main()