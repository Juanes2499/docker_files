# Guía: Usar cx_Oracle con Apache Spark

Esta guía explica cómo conectar Apache Spark con Oracle Database usando cx_Oracle en el entorno Docker.

## 📋 ¿Qué se ha instalado?

### 1. Oracle Instant Client 21.9
- **Ubicación**: `/opt/oracle/instantclient_21_9`
- **Propósito**: Cliente nativo de Oracle para conectividad
- **Componentes**: Basic + Development headers

### 2. cx_Oracle (Python)
- **Versión**: Última disponible via pip
- **Propósito**: Driver Python para Oracle Database
- **Ubicación**: Instalado en el entorno Python del contenedor

### 3. Oracle JDBC Driver (ojdbc8.jar)
- **Ubicación**: `/opt/spark/jars/ojdbc8.jar`
- **Propósito**: Driver JDBC para que Spark se conecte a Oracle
- **Versión**: Compatible con Oracle 12c+

## 🚀 Cómo usar

### Opción 1: Reconstruir los contenedores

```powershell
# Detener contenedores actuales
docker-compose down

# Reconstruir con Oracle support
docker-compose up --build
```

### Opción 2: Usar imagen pre-construida (recomendado para desarrollo)

Si ya tienes los contenedores funcionando, puedes instalar cx_Oracle en el contenedor running:

```powershell
# Conectar al contenedor Jupyter
docker exec -it spark-jupyter bash

# Instalar cx_Oracle
pip install cx_Oracle

# Verificar instalación
python -c "import cx_Oracle; print(cx_Oracle.version)"
```

## 📝 Ejemplos de Uso

### 1. Conexión directa con cx_Oracle

```python
import cx_Oracle

# Configurar conexión
dsn = cx_Oracle.makedsn("host", "1521", service_name="ORCL")
connection = cx_Oracle.connect(user="username", password="password", dsn=dsn)

# Ejecutar consulta
cursor = connection.cursor()
cursor.execute("SELECT SYSDATE FROM DUAL")
result = cursor.fetchone()
print(f"Fecha: {result[0]}")

# Cerrar conexión
cursor.close()
connection.close()
```

### 2. Spark con Oracle JDBC

```python
from pyspark.sql import SparkSession

# Crear sesión Spark con Oracle JDBC
spark = SparkSession.builder \
    .appName("Oracle Example") \
    .master("spark://spark-master:7077") \
    .config("spark.jars", "/opt/spark/jars/ojdbc8.jar") \
    .getOrCreate()

# Leer desde Oracle
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:oracle:thin:@host:1521:ORCL") \
    .option("dbtable", "your_table") \
    .option("user", "username") \
    .option("password", "password") \
    .option("driver", "oracle.jdbc.driver.OracleDriver") \
    .load()

df.show()
```

### 3. Escribir a Oracle

```python
# Escribir DataFrame a Oracle
df.write \
    .format("jdbc") \
    .option("url", "jdbc:oracle:thin:@host:1521:ORCL") \
    .option("dbtable", "target_table") \
    .option("user", "username") \
    .option("password", "password") \
    .option("driver", "oracle.jdbc.driver.OracleDriver") \
    .mode("overwrite") \
    .save()
```

## 🔧 Configuración de Conexión

### Variables de Entorno (Recomendado)

Agrega estas variables al `docker-compose.yml`:

```yaml
environment:
  - ORACLE_HOST=your_oracle_host
  - ORACLE_PORT=1521
  - ORACLE_SERVICE=ORCL
  - ORACLE_USER=your_username
  - ORACLE_PASSWORD=your_password
```

### En Python

```python
import os

oracle_config = {
    "host": os.getenv("ORACLE_HOST", "localhost"),
    "port": os.getenv("ORACLE_PORT", "1521"),
    "service_name": os.getenv("ORACLE_SERVICE", "ORCL"),
    "username": os.getenv("ORACLE_USER", "your_username"),
    "password": os.getenv("ORACLE_PASSWORD", "your_password")
}
```

## 📁 Archivos de Ejemplo

### Notebooks
- `oracle_connection_example.ipynb`: Ejemplos interactivos completos
- Ubicación: `/notebooks/oracle_connection_example.ipynb`

### Scripts de Jobs
- `oracle_test_job.py`: Script de prueba para conexiones Oracle
- Ubicación: `/jobs/oracle_test_job.py`

### Ejecutar trabajo de ejemplo

```powershell
# Desde PowerShell
docker exec spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --jars /opt/spark/jars/ojdbc8.jar \
    /opt/spark/jobs/oracle_test_job.py
```

## 🛠️ Optimizaciones para Producción

### 1. Configuración de Rendimiento

```python
df = spark.read \
    .format("jdbc") \
    .option("url", oracle_url) \
    .option("dbtable", "large_table") \
    .option("user", username) \
    .option("password", password) \
    .option("driver", "oracle.jdbc.driver.OracleDriver") \
    .option("fetchsize", "10000") \
    .option("batchsize", "10000") \
    .option("numPartitions", "8") \
    .option("partitionColumn", "id") \
    .option("lowerBound", "1") \
    .option("upperBound", "1000000") \
    .load()
```

### 2. Pooling de Conexiones

```python
# Para cx_Oracle
import cx_Oracle

# Crear pool de conexiones
pool = cx_Oracle.create_pool(
    user="username",
    password="password", 
    dsn="host:1521/ORCL",
    min=2,
    max=10,
    increment=1
)

# Usar conexión del pool
connection = pool.acquire()
# ... usar conexión ...
pool.release(connection)
```

## 🐛 Troubleshooting

### Error: "DPI-1047: Cannot locate an Oracle Client library"

```bash
# Verificar que Oracle Client esté instalado
echo $ORACLE_HOME
echo $LD_LIBRARY_PATH
ldconfig -p | grep oracle
```

### Error: "TNS:could not resolve the connect identifier"

- Verificar host, puerto y service name
- Probar conexión con `tnsping` si está disponible
- Usar IP en lugar de hostname

### Error: "ORA-12541: TNS:no listener"

- Verificar que Oracle database esté ejecutándose
- Verificar puerto (1521 por defecto)
- Verificar firewall/conectividad de red

### Error en Spark: "No suitable driver found"

```python
# Asegurar que el JAR esté en el classpath
spark = SparkSession.builder \
    .config("spark.jars", "/opt/spark/jars/ojdbc8.jar") \
    .config("spark.driver.extraClassPath", "/opt/spark/jars/ojdbc8.jar") \
    .config("spark.executor.extraClassPath", "/opt/spark/jars/ojdbc8.jar") \
    .getOrCreate()
```

## 📚 Recursos Adicionales

- [cx_Oracle Documentation](https://cx-oracle.readthedocs.io/)
- [Oracle JDBC Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/21/jjdbc/)
- [Spark JDBC Documentation](https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html)

## 🔒 Seguridad

### NO hagas esto en producción:
- Hardcodear credenciales en el código
- Usar passwords en texto plano en docker-compose.yml

### SÍ haz esto:
- Usar variables de entorno
- Usar Docker secrets
- Implementar conexiones SSL/TLS
- Rotar credenciales regularmente

```yaml
# Ejemplo con Docker secrets
services:
  spark-master:
    secrets:
      - oracle_password
    environment:
      - ORACLE_PASSWORD_FILE=/run/secrets/oracle_password

secrets:
  oracle_password:
    file: ./secrets/oracle_password.txt
```