FROM apache/airflow:2.7.3-python3.8

ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING="True" \
    AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags

WORKDIR /opt/airflow

USER airflow

COPY --chown=airflow:root requirements.txt requirements.dev.txt airflow-constraints.txt ./
RUN pip install -r requirements.txt -c airflow-constraints.txt --no-cache-dir

COPY --chown=airflow:root MANIFEST.in setup.py ./

COPY --chown=airflow:root version pyproject.toml ./

COPY --chown=airflow:root aiqst ./aiqst
COPY --chown=airflow:root dags ./dags

RUN pip install -e . -c airflow-constraints.txt --no-cache-dir
