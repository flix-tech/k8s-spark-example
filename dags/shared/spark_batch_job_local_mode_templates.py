properties = """
spark.sql.streaming.metricsEnabled=true
spark.master=local[6]
spark.driver.memory=4g
spark.driver.maxResultSize=2g
spark.hadoop.fs.s3a.multiobjectdelete.enable=false
spark.hadoop.fs.s3a.fast.upload=true
spark.sql.parquet.filterPushdown=true
spark.sql.parquet.mergeSchema=false
spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version=2
spark.speculation=false
spark.serializer=org.apache.spark.serializer.KryoSerializer
"""

spark_submit_sh = f"""
echo '{properties}' > /tmp/properties;
/opt/spark/bin/spark-submit \
--name $SERVICE_NAME \
--packages io.delta:delta-core_2.11:0.5.0 \
--conf spark.pyspark.python=/usr/bin/python3 \
--py-files $PY_FILES \
--properties-file /tmp/properties \
local://$PYTHON_FILE
"""