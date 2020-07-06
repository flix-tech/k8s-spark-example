# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
This is an example dag for using the Kubernetes Executor.
"""
import os

import airflow
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.kubernetes.pod_runtime_info_env import PodRuntimeInfoEnv

DAG_NAME = "historical_process"
ENV = os.environ.get("ENV")

properties = """
spark.executor.instances=6
spark.kubernetes.allocation.batch.size=5
spark.kubernetes.allocation.batch.delay=1s
spark.kubernetes.authenticate.driver.serviceAccountName=spark
spark.kubernetes.executor.lostCheck.maxAttempts=10
spark.kubernetes.submission.waitAppCompletion=false
spark.kubernetes.report.interval=1s
spark.kubernetes.pyspark.pythonVersion=3
spark.pyspark.python=/usr/bin/python3

#kubernetes resource managements
spark.kubernetes.driver.request.cores=10m
spark.kubernetes.executor.request.cores=50m
spark.executor.memory=500m
spark.kubernetes.memoryOverheadFactor=0.1

spark.kubernetes.executor.annotation.cluster-autoscaler.kubernetes.io/safe-to-evict=true
spark.sql.streaming.metricsEnabled=true
"""

historical_process_image = "dcr.flix.tech/data/flux/k8s-spark-example:latest"

envs = {
"SERVICE_NAME": f"historical_process_{ENV}",
"CONTAINER_IMAGE": historical_process_image,
"SPARK_DRIVER_PORT": "35000",
"APP_FILE": "/workspace/python/pi.py",
}

pod_runtime_info_envs = [
    PodRuntimeInfoEnv('MY_POD_NAMESPACE','metadata.namespace'),
    PodRuntimeInfoEnv('MY_POD_NAME','metadata.name'),
    PodRuntimeInfoEnv('MY_POD_IP','status.podIP')
]

spark_submit_sh = f"""
echo '{properties}' > /tmp/properties;
/opt/spark/bin/spark-submit \
--master k8s://https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT \
--deploy-mode client \
--name $SERVICE_NAME \
--conf spark.kubernetes.namespace=$MY_POD_NAMESPACE \
--conf spark.kubernetes.driver.pod.name=$MY_POD_NAME \
--conf spark.driver.host=$MY_POD_IP \
--conf spark.driver.port=$SPARK_DRIVER_PORT \
--conf spark.kubernetes.container.image=$CONTAINER_IMAGE \
--properties-file /tmp/properties \
$APP_FILE
"""

args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(2)
}

with DAG(
    dag_id=DAG_NAME,
    default_args=args,
    schedule_interval='30 0 * * *'
) as dag:

    # Limit resources on this operator/task with node affinity & tolerations
    historical_process = KubernetesPodOperator(
        namespace=os.environ['AIRFLOW__KUBERNETES__NAMESPACE'],
        name="historical-process",
        image=historical_process_image,
        image_pull_policy="IfNotPresent",
        cmds=["/bin/sh","-c"],
        arguments=[spark_submit_sh],
        env_vars=envs,
        service_account_name="airflow",
        resources={
            'request_memory': "1024Mi",
            'request_cpu': "100m"
            },
        task_id="historical-process-1",
        is_delete_operator_pod=True,
        in_cluster=True,
        hostnetwork=False,
        #important env vars to run spark submit
        pod_runtime_info_envs=pod_runtime_info_envs
    )
    historical_process