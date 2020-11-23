 ## Consumption Calculator 

This is a sample **pyspark application**, containerized to execute on different container orchastation solutions.

This app processing sales.csv, product.csv,store.csv,calendar.csv and generates consumption weekly aggregrates as a json output 

Application is modularized and containeraized for easy of CI/CD and options to deploy on on-premise or cloud.


### Prerequistes

### Local Development
* Docker Engine, Docker cli, SWARM<sup>*</sup> 
### Tools
  * docker cli,Docker-compose , Helm
### Infra
* KIND<sup>*</sup> - for local k8s develoment 
* AWS<sup>*</sup>
    * eksctl - to spin up EKS on AWS,  helm<sup>*</sup>
* Linux Node(Ubuntu),or WLS;windows linux subsystem for dev work.

this Spark-app uses [spark-base:3.0.1-hadoop3.2 ](https://github.com/MrDaggubati/Dockerfiles/tree/main/spark)  as base layer to build on further Python application. 

docker-compose.yml can be ued to spin up a local cluster on docker engine

You can build and launch your Python application on a Spark cluster by extending this image with your sources. 
uses pip -r requirements.txt file in the root of the app folder for dependency management.


steps to  run this app.

1. pull docker images and dependencies using docker-compose.yml from **spark** DockerFiles folder to create a cluster.
1. you can run this as a local cluster or a self contained spark cluster & app
   1. using Docker engine on single node

      1. pull docker images fromdocker hub, or clone the repo  
      1. spins up a local custer 

         ```  docker-compose up -d & ```

      1. check local cluster up and running 

         ```docker-compose ps | grep spark```

        1. either pusll or clone the [pyspark-app](https://github.com/mrdaggubati/pyspark-app) repo 
      1. Deploy pyspark app in interactive mode
            
         ``` docker build --rm -t mrdaggubati/pyspark-app .```
      1. run the application using below  command
         ``` docker run -it --network=spark_default --link spark-master:spark-master -e ENABLE_INIT_DAEMON=false mrdaggubati/pyspark-app ```

   1. if AWS access if available then,
      spin up an AWS EKS fargate cluster(managed kubernetes instances) using eksctl refer [[aws-eks-eksctl.md](https://github.com/mrdaggubati/pyspark-app/aws-eks-eksctl.md) ]

      * **helm charts** -- WIP
      
   1. using KIND ;

      Altenratively , you could deploy the spark standalone<sup>*</sup> cluster on a  multinode pseduo k8s Local dev environment 
      
         -- where is that document! 
      * helm charts / k8s manifests still WIP

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

        docker run -it --network=spark_spark-network --link spark-master:spark-master -e ENABLE_INIT_DAEMON=false mrdaggubati/spark-test-app
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

# WIP
  1. **helm charts**
  1. **K8S deployment artefacts**
  1. App logic ; to read and write into object stores



**issues**

* having multiple images and  environment variables initialization across image builds and lauers + COPY ONBUILD , RUN directives created issues with environement variable propagation chain , took sometime to figure it out
* so, i have modified base image, discarded **submit** template to build the app starting with spark-base as base layer for the app


**Credits**

 Big Data EUROPE ;  for base images and spark-cluster templates.

