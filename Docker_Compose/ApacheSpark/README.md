# Apache Spark Docker Environment

Este proyecto proporciona un entorno completo de Apache Spark usando Docker, que incluye:

- **Spark Master**: Nodo maestro del cluster
- **Spark Workers**: Nodos trabajadores (2 por defecto)
- **Jupyter Notebook**: Interfaz interactiva para desarrollar con Spark

## Estructura del Proyecto

```
ApacheSpark/
├── docker-compose.yml          # Configuración de servicios Docker
├── Dockerfile                  # Imagen base para todos los servicios
├── README.md                   # Este archivo
├── conf/                       # Configuraciones de Spark
│   ├── spark-defaults.conf     # Configuración principal de Spark
│   └── log4j.properties        # Configuración de logging
├── scripts/                    # Scripts de utilidad
│   └── entrypoint.sh          # Script de entrada para contenedores
├── data/                      # Directorio para datos (montado como volumen)
├── notebooks/                 # Jupyter notebooks (montado como volumen)
│   └── spark_example.ipynb    # Notebook de ejemplo
└── jobs/                      # Scripts de trabajos Spark (montado como volumen)
    └── example_job.py         # Trabajo de ejemplo
```

## Requisitos Previos

- Docker Desktop instalado y ejecutándose
- Al menos 4GB de RAM disponible para Docker
- Puertos disponibles: 8080, 7077, 4040, 8081, 8082, 8888

## Instalación y Uso

### 1. Construir e Iniciar el Cluster

```powershell
# Navegar al directorio del proyecto
cd "c:\Users\juan.nichoy\Documents\Proyectos\XM\PoCs\ApacheSpark"

# Construir las imágenes y iniciar todos los servicios
docker-compose up --build
```

### 2. Verificar que los Servicios Estén Ejecutándose

Una vez que todos los contenedores estén iniciados, puedes acceder a:

- **Spark Master UI**: http://localhost:8080
- **Worker 1 UI**: http://localhost:8081
- **Worker 2 UI**: http://localhost:8082
- **Jupyter Notebook**: http://localhost:8888
- **Spark Application UI**: http://localhost:4040 (cuando haya aplicaciones ejecutándose)

### 3. Usar Jupyter Notebook

1. Abre tu navegador en http://localhost:8888
2. Abre el notebook `spark_example.ipynb`
3. Ejecuta las celdas para ver ejemplos de uso de Spark

### 4. Ejecutar Trabajos de Spark

Para ejecutar un trabajo de Spark desde la línea de comandos:

```powershell
# Ejecutar el trabajo de ejemplo
docker exec spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --py-files /opt/spark/jobs/example_job.py \
    /opt/spark/jobs/example_job.py
```

### 5. Acceder a los Contenedores

Para acceder a un contenedor específico:

```powershell
# Acceder al contenedor master
docker exec -it spark-master bash

# Acceder al contenedor de Jupyter
docker exec -it spark-jupyter bash
```

## Comandos Útiles

### Gestión del Cluster

```powershell
# Iniciar todos los servicios
docker-compose up -d

# Detener todos los servicios
docker-compose down

# Ver logs de un servicio específico
docker-compose logs spark-master

# Reiniciar un servicio
docker-compose restart spark-master

# Escalar workers (por ejemplo, a 3 workers)
docker-compose up -d --scale spark-worker-1=3
```

### Monitoreo

```powershell
# Ver el estado de los contenedores
docker-compose ps

# Monitorear recursos utilizados
docker stats

# Ver logs en tiempo real
docker-compose logs -f
```

## Configuración Personalizada

### Ajustar Recursos de Workers

Puedes modificar la memoria y cores de los workers editando el archivo `docker-compose.yml`:

```yaml
environment:
  - SPARK_WORKER_CORES=4      # Cambiar número de cores
  - SPARK_WORKER_MEMORY=4g    # Cambiar memoria asignada
```

### Agregar Más Workers

Para agregar más workers, puedes duplicar la configuración de `spark-worker-2` en el `docker-compose.yml` y cambiar los nombres y puertos.

### Configuración de Spark

Modifica el archivo `conf/spark-defaults.conf` para ajustar la configuración de Spark según tus necesidades.

## Volúmenes de Datos

Los siguientes directorios están montados como volúmenes y son persistentes:

- `./data`: Para almacenar datasets y resultados
- `./notebooks`: Para notebooks de Jupyter
- `./jobs`: Para scripts de trabajos Spark

## Resolución de Problemas

### Puerto ya en uso
Si algún puerto está en uso, puedes cambiar los mapeos de puertos en `docker-compose.yml`.

### Memoria insuficiente
Si experimentas problemas de memoria, reduce la memoria asignada a los workers o aumenta la memoria disponible para Docker.

### Contenedores no inician
Verifica los logs con `docker-compose logs [service-name]` para identificar el problema.

## Desarrollo

### Agregar Dependencias Python

Para agregar nuevas librerías Python, modifica el `Dockerfile`:

```dockerfile
RUN pip3 install pyspark jupyter notebook pandas numpy matplotlib seaborn tu-nueva-libreria
```

Luego reconstruye las imágenes:

```powershell
docker-compose build --no-cache
```

### Usar con VS Code

Puedes usar la extensión "Remote - Containers" de VS Code para desarrollar directamente dentro de los contenedores.

## Ejemplos de Uso

### Cargar un Dataset CSV

```python
# En Jupyter Notebook
df = spark.read.option("header", "true").csv("/opt/spark/data/tu_archivo.csv")
df.show()
```

### Procesar Datos en Batch

```python
# Procesamiento de grandes volúmenes de datos
large_df = spark.read.parquet("/opt/spark/data/large_dataset.parquet")
result = large_df.groupBy("category").agg({"amount": "sum", "count": "count"})
result.write.mode("overwrite").parquet("/opt/spark/data/results.parquet")
```

¡Disfruta trabajando con Apache Spark en Docker!