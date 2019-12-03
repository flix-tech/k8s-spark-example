# Spark on Kubernetes - example app 

This is an example project running a Spark app on Kubernetes. It runs a PySpark job as spark driver deployment on Kubernetes. More information [here](https://spark.apache.org/docs/latest/running-on-kubernetes.html).

The application base image relies on the spark image built on [here](https://git.flix.tech/data/flux/web-tracking/spark-on-kubernetes-docker-image).

## run app locally

Install local Kubernetes cluster first. Use [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/).

Install `task` build tools [task](https://taskfile.dev/#/installation).

Run locally:
```shell script
task run.local
```
Undeploy locally:
```shell script
task spark.helm.undeploy
```
![](./k8s-spark.gif)

## deploy on EKS Kubernetes cluster
Edit `.gitlab-ci.yml` file to adapt it to deploy to your own k8s namespace, please read team plateform documentation for details about gitlab runner and Kubernetes.

Create a branch will automatically deploy it on ew1d2 cluster, data-flux-dev namespace. Merge branch will deploy code on data-flux-stg and then to ew1p3 data-flux namespace.