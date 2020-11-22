FROM mrdaggubati/spark-base:3.0.1-hadoop3.2 
#FROM mrdaggubati/pyspark-app-base:latest

COPY requirements.txt /app/requirements.txt
WORKDIR /app/
RUN  pip3 install -r requirements.txt

ENV SPARK_MASTER_NAME spark-master
ENV SPARK_MASTER_PORT 7077
ENV SPARK_APPLICATION_JAR_LOCATION /app/application.jar
ENV SPARK_APPLICATION_PYTHON_LOCATION /app/app.py
ENV SPARK_APPLICATION_MAIN_CLASS my.main.Application
ENV SPARK_APPLICATION_ARGS ""
ENV SPARK_SUBMIT_ARGS ""
ENV SPARK_APPLICATION_ARGS  ""

COPY template.sh /template.sh
COPY submit.sh /submit.sh
RUN chmod +x /template.sh && chmod +x /submit.sh

COPY /app/conf/log4j.properties  /spark/conf/log4j.properties

COPY app /app



CMD ["/bin/bash", "/template.sh"]