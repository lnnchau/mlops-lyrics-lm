FROM apache/airflow:2.6.0-python3.10
COPY requirements.airflow.txt /
USER airflow
RUN pip install --no-cache-dir -r /requirements.airflow.txt
RUN bentoctl operator install aws-lambda

USER root
RUN chmod +x /home/airflow/bentoml