#!/usr/bin/env bash
: "${PROPERTIES_FILE:="/opt/spark.properties"}"
: "${SPARK_DRIVER_PORT:="35861"}"
: "${PYTHON_FILE:="/opt/example/python/pi.py"}"
: "${SPARK_MODE:="client"}"

export \
  PROPERTIES_FILE \
  SPARK_DRIVER_PORT \
  PYTHON_FILE \
  SPARK_MODE \

function ensure() {
    ## Determine if a bash variable is empty or not ##
    local env_value=$(printenv $1)
    echo "$1=$(printenv $1)"
    printenv $1 > /dev/null
    if [[ -z "$env_value" || $? -ne 0 ]]; then
        echo "$1 is unset or set to the empty string";
        exit 1;
    fi
}

function ensure_clientmode() {
    ensure KUBERNETES_SERVICE_HOST
    ensure KUBERNETES_SERVICE_PORT
    ensure SERVICE_NAME
    ensure MY_POD_NAMESPACE
    ensure MY_POD_NAME
    ensure MY_POD_IP
    ensure SPARK_DRIVER_PORT
    ensure CONTAINER_IMAGE
    ensure PROPERTIES_FILE
    ensure PY_FILES
    ensure PYTHON_FILE
}

function ensure_localmode() {
    ensure SERVICE_NAME
    ensure PY_FILES
    ensure PYTHON_FILE
}

ensure SPARK_MODE

set -o xtrace

case "${SPARK_MODE}" in
  local)
    ensure_localmode;
    /opt/spark/bin/spark-submit \
    --name $SERVICE_NAME \
    --conf spark.pyspark.python=/usr/bin/python3 \
    --properties-file $PROPERTIES_FILE \
    --py-files $PY_FILES \
    $PYTHON_FILE
    ;;
  client)
    ensure_clientmode;
    #spark-submit excecuted to spin up spark driver
    #MY_POD_NAMESPACE/MY_POD_IP/MY_POD_IP get from pod inspection in deployment/pod
    #KUBERNETES_SERVICE_HOST/KUBERNETES_SERVICE_PORT are native k8s pod env variables
    #SERVICE_NAME is given by deployment, set as the service name
    #CONTAINER_IMAGE is used for executor pod
    #PROPERTIES_FILE is the spark properties
    #PYTHON_FILE is the spark application file
    /opt/spark/bin/spark-submit \
    --master k8s://https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT \
    --deploy-mode client \
    --name $SERVICE_NAME \
    --conf spark.kubernetes.namespace=$MY_POD_NAMESPACE \
    --conf spark.kubernetes.driver.pod.name=$MY_POD_NAME \
    --conf spark.driver.host=$MY_POD_IP \
    --conf spark.driver.port=$SPARK_DRIVER_PORT \
    --conf spark.kubernetes.container.image=$CONTAINER_IMAGE \
    --conf spark.pyspark.driver.python=/usr/bin/python3 \
    --properties-file $PROPERTIES_FILE \
    --py-files $PY_FILES \
    $PYTHON_FILE
    ;;
  *)
    echo $"Usage: $0 {local|cluster}"
    exit 1
esac
