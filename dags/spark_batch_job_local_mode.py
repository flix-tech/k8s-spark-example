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
from shared.spark_batch_job_local_mode_templates import spark_submit_sh
from shared.utils import read_packaged_file

DAG_NAME = "spark_batch_job_local_mode"
ENV = os.environ.get("ENV")

docker_image = "dcr.flix.tech/data/flux/k8s-spark-example:latest"

envs = {
"SERVICE_NAME": DAG_NAME,
"CONTAINER_IMAGE": docker_image,
"PY_FILES": "/workspace/dist/libs.zip,/workspace/dist/dependencies.zip",
"PYTHON_FILE": "/workspace/python/pi.py",
}

args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(2)
}

# base path returned zip dag path
base_path = os.path.split(__file__)[0]

plain_txt = read_packaged_file(
    f"{base_path}/plain_files/plain.txt"
)

with DAG(
    dag_id=DAG_NAME,
    default_args=args,
    schedule_interval='30 0 * * *'
) as dag:
    # Use the zip binary, which is only found in this special docker image
    read_local_file = BashOperator(
        task_id='read_local_file',
        bash_command=f"echo {plain_txt}")
    # Limit resources on this operator/task with node affinity & tolerations
    spark_batch_job_local_mode = KubernetesPodOperator(
        namespace=os.environ['AIRFLOW__KUBERNETES__NAMESPACE'],
        name="spark_batch_job_local_mode",
        image=docker_image,
        image_pull_policy="IfNotPresent",
        cmds=["/bin/sh","-c"],
        arguments=[spark_submit_sh],
        env_vars=envs,
        resources={
            'request_memory': "4024Mi",
            'request_cpu': "100m"
            },
        task_id="spark_batch_job_local_mode",
        is_delete_operator_pod=True,
        in_cluster=True,
        hostnetwork=False,
    )

    read_local_file, spark_batch_job_local_mode