# Amazon EKS cluster - eksctl 
using eksctl on AWS Fargate and use ALB Ingress Controller for loadbalancing 

To execute this, your environment must be having eksctl, awscli configured and having access aws through cli
folllow for instrructions

* eksctl, awscli, optionally an aws sts token

1.  create cluster using eksctl

   
    # creating cluster usig cli
    ```
    eksctl create cluster \
    --name <my-cluster> \
    --version <1.18> \
    --region <us-west-2> \
    --nodegroup-name <linux-nodes> \
    --nodes <3> \
    --nodes-min <1> \
    --nodes-max <4> \
    --with-oidc \
    --ssh-access \
    --ssh-public-key <name-of-ec2-keypair> \
    --managed
    ```
   # alternatively you could create using config file.

    below is the sample for creating using config file ; 
    refer https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html
    ---
  # An example of ClusterConfig with a normal nodegroup and a Fargate profile.
    ---
    apiVersion: eksctl.io/v1alpha5
    kind: ClusterConfig

    metadata:
    name: fargate-cluster
    region: us-west-2

    nodeGroups:
    - name: ng-1
        instanceType: t2.medium
        desiredCapacity: 2

    fargateProfiles:
    - name: fp-default
        selectors:
        # All workloads in the "default" Kubernetes namespace will be
        # scheduled onto Fargate:
        - namespace: default
        # All workloads in the "kube-system" Kubernetes namespace will be
        # scheduled onto Fargate:
        - namespace: kube-system
    - name: fp-dev
        selectors:
        # All workloads in the "dev" Kubernetes namespace matching the following
        # label selectors will be scheduled onto Fargate:
        - namespace: dev
            labels:
            env: dev
            checks: passed


   ``` eksctl create cluster --config-file fargate-profile-config.yml ```


2. Once cluster is created, create an oidc provider; this is basically to use web applications login authentication
   using thrid party authentication providers

   ```bash
    $ eksctl --region $REGION_NAME \
    utils associate-iam-oidc-provider \
    --cluster atinfer-eks-cluster \
    --approve
   ```


    Next create a service account, attache a IAM ROLE with policies that gives other AWS
    services access to the service account; services such as AWS RDS,S3 etc.. 

    

 3.  appply iam policy that lets ec2 cluster required role priviliges.
  
    create policy for  aws alb ingress controller

    ```sh
    $ aws iam create-policy \
    --policy-name ALBIngressControllerIAMPolicy \
    --policy-document aws-alb-ingress-controller-iam-policy.json
    ```
 4.  create a service account(**alb-ingress-controller**)
     for this cluster and attach the policy that has been created in earlier step

    ```sh
    $ eksctl --region ap-west-2 \
    create iamserviceaccount \
    --name alb-ingress-controller \
    --namespace kube-system \
    --cluster atinfer-eks-cluster \
    --attach-policy-arn arn:aws:iam::${UR_ARN}XXXX:policy/ALBIngressControllerIAMPolicy \
    --approve
    ```

    replace that policy arn from actual poliy that was created earlier.


5.  Create a service account, cluster role, and cluster role binding for the ALB Ingress Controller to use with the following command. 
    use provided rbad file or download from kubernetes sigs
    ```sh
    $ kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.4/docs/examples/rbac-role.yaml
    
    $ kubectl apply -f rbac-aws-alb-ingress-controller.yml
    ```

6.   run the nginx deployment and service

7.   Download the `alb-ingress-controller.yaml`

    ```sh
    $ wget https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.4/docs/examples/alb-ingress-controller.yaml
    ```


edit the yaml and update the following arguments

- **--cluster-name**=atinfer-eks-cluster
- **--aws-vpc-id**=vpc-xxxxxxxxxxxx
- **--aws-region**=us-west-2

And make sure to specify the `ip` target-type



 deploy the **alb-ingress-controller** now

 ```sh
    $ kubectl apply -f alb-ingress-controller.yaml
 ```

10. deploy the ingress object

```sh
$ kubectl apply -f nginx-ingress.yaml
```

11. lookup the alb-ingress-controller pod name and watch its logs

```sh
# lookup the pod id
kubectl get po -A  | grep alb-ingress
# logs -f to watch the pod logs. Make sure you specify correct pod name
kubectl -n kube-system logs -f po/alb-ingress-controller-78cb78cffb-ddkj8
```



![](images/eks-fargate-06.png)



12. Now describe the ingress object to find out the **ALB DNS name** and curl the ALB

![](images/eks-fargate-07.png)

You will see the welcome message from nginx.

#deploy a test manifest to check if the eks deployment done sof ar is working or not by running sample app.

use any sample app that you could get hold on and safe. 

## clean up

```sh
kubectl delete -f XXX-service.yaml
kubectl delete -f XXX-ingress.yaml
kubectl delete -f XXX-deployment.yaml
kubectl delete -f XXX-namespace.yaml
kubectl delete -f alb-ingress-controller.yml
eksctl --region us-west-2 delete cluster --name atinfer-eks-cluster
```
