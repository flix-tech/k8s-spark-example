FROM gcr.io/spark-operator/spark-py:v2.4.4

COPY . /opt/example

WORKDIR /opt/example

CMD ["/opt/example/scripts/entrypoint.sh"]