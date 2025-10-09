#!/bin/bash

# Script de entrada para contenedores Spark

set -e

# Crear y configurar directorios de trabajo
mkdir -p /opt/spark/work /opt/spark/logs /opt/spark/tmp
chmod 755 /opt/spark/work /opt/spark/logs /opt/spark/tmp

# Función para esperar que un servicio esté disponible
wait_for_service() {
    local host=$1
    local port=$2
    echo "Waiting for $host:$port to be available..."
    while ! nc -z $host $port; do
        sleep 1
    done
    echo "$host:$port is available"
}

# Configurar según el modo
case $SPARK_MODE in
    "master")
        echo "Starting Spark Master..."
        exec $SPARK_HOME/bin/spark-class org.apache.spark.deploy.master.Master \
            --host $SPARK_MASTER_HOST \
            --port $SPARK_MASTER_PORT \
            --webui-port 8080
        ;;
    "worker")
        echo "Starting Spark Worker..."
        wait_for_service spark-master 7077
        exec $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker \
            $SPARK_MASTER_URL \
            --cores $SPARK_WORKER_CORES \
            --memory $SPARK_WORKER_MEMORY \
            --webui-port 8081 \
            --host $SPARK_LOCAL_IP
        ;;
    "jupyter")
        echo "Starting Jupyter Notebook with Spark..."
        wait_for_service spark-master 7077
        export PYSPARK_DRIVER_PYTHON=jupyter
        export PYSPARK_DRIVER_PYTHON_OPTS='notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password=""'
        export PYSPARK_PYTHON=python3
        export SPARK_DRIVER_HOST=$SPARK_DRIVER_HOST
        cd /opt/spark/notebooks
        exec jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password=""
        ;;
    *)
        echo "Unknown SPARK_MODE: $SPARK_MODE"
        exit 1
        ;;
esac