import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from aiqst.scripts.insert_data import perform_bulk_insert

default_args = {
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=1),
}

def run_alembic_initial_migration():
    import subprocess

    subprocess.run(["alembic", "upgrade", "head"])

with DAG(
    dag_id="initial_data_load",
    start_date=datetime.datetime(2023, 12, 4),
    catchup=False,
    schedule=None,
    default_args=default_args,
    tags=["initial load"],
    render_template_as_native_obj=True,
) as dag:
    start = EmptyOperator(
        task_id="start",
    )
    create_schema = PostgresOperator(
        task_id = 'create_schema',
        sql = "CREATE SCHEMA IF NOT EXISTS source;"
    )
    run_alembic_migration = PythonOperator(
         task_id='run_alembic_migration',
         python_callable=run_alembic_initial_migration,
         dag=dag,
    )
    insert_data = PythonOperator(
        task_id="insert_data",
        python_callable=perform_bulk_insert,
        dag=dag,
    )
    end = EmptyOperator(
        task_id="end",
    )

    start >> create_schema >> run_alembic_migration>> insert_data >> end
