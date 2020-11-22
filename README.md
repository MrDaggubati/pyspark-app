
 ## Consumption Calculator 

This is a sample **pyspark application**, containerized to execute on different container orchastation solutions.

### Prerequistes

### Local Development
* Docker Engine, Docker cli, SWARM<sup>*</sup> 
* KIND<sup>*</sup> - for local k8s develoment 
### container soltutions
* Docker, Docker-compose, Docker CLI
* eksctl - to spin up EKS on AWS,  helm<sup>*</sup>
### Tools
  * Python >3
  * docker cli
### Infra
* AWS<sup>*</sup>
* Linux Node Ubuntu



Spark Python template

The Spark Python app uses  spark-base:3.0.1-hadoop3.2 as base layer to build on further Python application. 

See big-data-europe/docker-spark README for a description how to setup a Spark cluster.
Package your application using pip

You can build and launch your Python application on a Spark cluster by extending this image with your sources. 
uses pip -r requirements.txt file in the root of the app folder for dependency management.


steps to  run this app.

1. pull docker images and dependencies using docker-compose.yml from **spark** DockerFiles folder to create a cluster.
1. you can run this as a local cluster or a self contained spark cluster & app
   1. using Docker engine on single node
   1. using Docker Swarm
   1. using KIND ; multinode pseduo k8s cluster on docker node
   1. using ekctl on AWS EKS, managed kubernetes instances


2. To make it as your own pyspark app 
    extend/modify the docker image as you feel convinent
    1. copy the a *Dockerfile* and other folder setup, Dockerfile in the root folder of your project 
    2. keep requirements.txt in the first layer, list your dependencies;to avoid cache-invalidations.
    
    1. extend/modify below environment variables as needed.

        SPARK_MASTER_NAME (default: spark-master)
        SPARK_MASTER_PORT (default: 7077)
        SPARK_APPLICATION_PYTHON_LOCATION (default: /app/app.py)
        SPARK_APPLICATION_ARGS

        Build and run the image; give any funkyname you want.

        ```
        docker build --rm -t mrdaggubati/spark-test-app:pyspark .

        docker run -it --network=spark_spark-network --link spark-master:spark-master -e ENABLE_INIT_DAEMON=false mrdaggubati/spark-test-app:pyspar
        ```
       
1. Test the app by running using below commands

   **check subnets** 
   *<sub>--network=spark301_default</sub>*

    Make not of the network name in which the cluster was initiazed; use services docker-compose for better control

    ** to run in it manually

     ```
      docker build --rm -t mrdaggubati/sparkyx .
      docker run --name my-spark-app --network=spark301_default -e ENABLE_INIT_DAEMON=false --link spark-master:spark-master -d mrdaggubati/sparkyx
   ```

### check the app

### issues/precautions
i have taken Spark base as base image for sample application and modified submit.sh and Dockerfile to suite the requirements.

1. Keep requirements.text in top layers and COPY app folder as the last to reduce re-installs.
1. instaling pandas is a mess on this alpine image base, python-3.8-slim buster can work but it dropped curl and other useful tools from the repo, then you got to rework base with relavant package managers and libs
1. spark job history server docker iages yet to be cooked/ordered/integrated from opensources.
1. ....



**Credits**

Thanks to Big Data EUROPE for base images and template.

* having multiple images and  environment variables initialization across image builds and lauers + COPY ONBUILD , RUN directives created issues with environement variable propagation chain , took sometime to figure it out
* so, i have modified base image, discarded **submit** template to build the app starting with spark-base as base layer for the app
