import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

default_args = {
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=1),
}

with DAG(
    dag_id="dummy",
    start_date=datetime.datetime(2023, 8, 10),
    catchup=False,
    schedule=None,
    default_args=default_args,
    params={
        "param1": "value1", # placeholder
    },
    tags=["test"],
    render_template_as_native_obj=True,
) as dag:
    start = EmptyOperator(
        task_id="start",
    )
    task1 = PythonOperator(
        task_id="task1",
        python_callable=lambda: {"status": "success"},
    )
    end = EmptyOperator(
        task_id="end",
    )

    start >> task1 >> end
