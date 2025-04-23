from datetime import timedelta, datetime
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    'sample',
    default_args=default_args,
    description= "A simple Airflow DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 9, 16),
    catchup=False,
    tags=['example']
    ) as dag:

    task1 = BashOperator(
        task_id='print_date',
        bash_command='date'
    )

    task2 = BashOperator(
        task_id='sleep',
        depends_on_past=False,
        bash_command='sleep 5',
        retries=2
    )


task1 >> task2