#!/bin/bash


/wait-for-step.sh

#env
echo " **************************************** " 

#define your workload submit options here
submit_args=""

#define your application specific configs, or metadata etc here
appl_args="" #" --files /app/data/calendar.csv,/app/data/sales.csv,/app/data/products.csv,/app/data/products.csv,/app/data/store.csv"

export SPARK_HOME=/spark
export ENABLE_INIT_DAEMON "false"

# export SPARK_MASTER_URL=spark://${SPARK_MASTER_NAME}:${SPARK_MASTER_PORT}
#export SPARK_APPLICATION_PYTHON_LOCATION="/app/app.py"

export SPARK_MASTER_URL="local[8]"

export SPARK_APPLICATION_ARGS=$appl_args
export SPARK_SUBMIT_ARGS=""
export SPARK_APPLICATION_JAR_LOCATION=""

echo "deployment mode  == ${SPARK_APPLICATION_PYTHON_LOCATION} to Spark master ${SPARK_MASTER_URL}"
echo "Passing APP arguments " ${SPARK_APPLICATION_ARGS}
echo "Passing SUBMIT arguments " ${SPARK_SUBMIT_ARGS}
echo "<<MARKER 3 >> This one ${SPARK_APPLICATION_PYTHON_LOCATION} " 


/execute-step.sh
if [ -f "${SPARK_APPLICATION_JAR_LOCATION}" ]; then
    echo "Submit application ${SPARK_APPLICATION_JAR_LOCATION} with main class ${SPARK_APPLICATION_MAIN_CLASS} to Spark master ${SPARK_MASTER_URL}"
    echo "Passing arguments ${SPARK_APPLICATION_ARGS}"
    /spark/bin/spark-submit \
        --class ${SPARK_APPLICATION_MAIN_CLASS} \
        --master ${SPARK_MASTER_URL} \
        ${SPARK_SUBMIT_ARGS} \
        ${SPARK_APPLICATION_JAR_LOCATION} ${SPARK_APPLICATION_ARGS}
else
    if [ -f "${SPARK_APPLICATION_PYTHON_LOCATION}" ]; then
        echo "Submit application ${SPARK_APPLICATION_PYTHON_LOCATION} to Spark master   ::   ${SPARK_MASTER_URL}"
        echo "Passing APP arguments ${SPARK_APPLICATION_ARGS}"
        echo "Passing SUBMIT arguments " ${SPARK_SUBMIT_ARGS}
        PYSPARK_PYTHON=python3 /spark/bin/spark-submit \
            --master ${SPARK_MASTER_URL} \
            ${SPARK_SUBMIT_ARGS} \
            ${SPARK_APPLICATION_PYTHON_LOCATION} ${SPARK_APPLICATION_ARGS}

        
    else
        echo "Not recognized application."
    fi
fi

/finish-step.sh

pwd

ls -lrta /app/consumption/consumption/