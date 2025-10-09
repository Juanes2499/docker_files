# Usar la imagen base de Ubuntu
FROM ubuntu:20.04

# Evitar prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias necesarias (incluyendo para Oracle)
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    python3 \
    python3-pip \
    wget \
    curl \
    procps \
    netcat \
    unzip \
    libaio1 \
    && rm -rf /var/lib/apt/lists/*

# Configurar JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Instalar Oracle Instant Client usando método básico
ENV ORACLE_HOME=/opt/oracle/instantclient
ENV LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
ENV PATH=$PATH:$ORACLE_HOME

# Crear directorio para Oracle y usar curl con opciones específicas
RUN mkdir -p /opt/oracle \
    && cd /opt/oracle \
    && curl -L -o instantclient-basic.zip "https://download.oracle.com/otn_software/linux/instantclient/1912000/instantclient-basic-linux.x64-19.12.0.0.0dbru.zip" \
    && curl -L -o instantclient-devel.zip "https://download.oracle.com/otn_software/linux/instantclient/1912000/instantclient-sdk-linux.x64-19.12.0.0.0dbru.zip" \
    && unzip instantclient-basic.zip \
    && unzip instantclient-devel.zip \
    && mv instantclient_19_12 instantclient \
    && rm -f instantclient-basic.zip instantclient-devel.zip \
    && echo $ORACLE_HOME > /etc/ld.so.conf.d/oracle-instantclient.conf \
    && ldconfig

# Descargar e instalar Apache Spark
ENV SPARK_VERSION=3.5.2
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark

RUN wget https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} \
    && rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Configurar PATH
ENV PATH=$PATH:${SPARK_HOME}/bin:${SPARK_HOME}/sbin

# Descargar Oracle JDBC driver para Spark
RUN cd ${SPARK_HOME}/jars \
    && wget https://download.oracle.com/otn-pub/otn_software/jdbc/217/ojdbc8.jar

# Instalar dependencias de Python
RUN pip3 install pyspark jupyter notebook pandas numpy matplotlib seaborn cx_Oracle sqlalchemy

# Crear directorios de trabajo
RUN mkdir -p /opt/spark/data /opt/spark/notebooks /opt/spark/jobs /opt/spark/logs /opt/spark/work /opt/spark/tmp \
    && chmod 755 /opt/spark/data /opt/spark/notebooks /opt/spark/jobs /opt/spark/logs /opt/spark/work /opt/spark/tmp

# Copiar scripts de configuración
COPY scripts/ /opt/spark/scripts/
COPY conf/ /opt/spark/conf/

# Hacer ejecutables los scripts
RUN chmod +x /opt/spark/scripts/*.sh

# Configurar el directorio de trabajo
WORKDIR /opt/spark

# Exponer puertos
EXPOSE 7077 7078 8080 8081 4040 8888

# Script de entrada
ENTRYPOINT ["/opt/spark/scripts/entrypoint.sh"]