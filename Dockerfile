FROM gcr.io/spark-operator/spark-py:v2.4.4

# copy Python dependecies and libs
COPY ./dist/dependencies.zip /workspace/dist/dependencies.zip
COPY ./dist/libs.zip /workspace/dist/libs.zip

# copy all Spark jobs
COPY ./python/ /workspace/python/

WORKDIR /workspace

# provide entrypoint file
COPY ./scripts/entrypoint.sh /workspace/scripts/entrypoint.sh

CMD ["/workspace/scripts/entrypoint.sh"]
