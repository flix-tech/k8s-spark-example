properties = """
spark.executor.instances=2
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
--py-files $PY_FILES \
--properties-file /tmp/properties \
local://$PYTHON_FILE
"""