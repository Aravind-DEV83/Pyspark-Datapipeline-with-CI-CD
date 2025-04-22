from datetime import datetime, timedelta
from airflow import DAG
from airflow.models.variable import Variable
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocSubmitJobOperator
)

# GCP Variables
config = Variable.get('configurations', deserialize_json=True)
PROJECT_ID=config['project_id']
REGION=config['region']
CLUSTER_NAME=config['cluster_name']
BUCKET_NAME='pyspark-jobs-omega-baton'
MAIN_PYSPARK_URI = f'gs://{BUCKET_NAME}/jobs/gcs_to_bq/job.py'
PY_FILES=f'gs://{BUCKET_NAME}/jobs/gcs_to_bq/transformations.py'
JARS = ['gs://spark-lib-omega-baton/gcs/gcs-connector-hadoop3-latest.jar']

#Define default args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'email_on_retry': False,
    'email_on_failure': False,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 4, 9)
}

with DAG(
    dag_id='Production_Pipeline_DAG',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=['production']
) as dag:
    
    start_pipeline = EmptyOperator(
        task_id='start_production_pipeline'
    )

    run_unit_tests = DataprocSubmitJobOperator(
        task_id='run_unit_tests',
        region=REGION,
        project_id=PROJECT_ID,
        job={
            "reference": {"project_id": PROJECT_ID},
            "placement": {"cluster_name": CLUSTER_NAME},
            "main_python_file_uri": f'gs://{BUCKET_NAME}/tests/unit/test_job.py',
            "python_file_uris": PY_FILES,
        }
    )

    run_integration_tests = DataprocSubmitJobOperator(
        task_id='run_integration_tests',
        region=REGION,
        project_id=PROJECT_ID,
        job={
            "reference": {"project_id": PROJECT_ID},
            "placement": {"cluster_name": CLUSTER_NAME},
            "main_python_file_uri": f'gs://{BUCKET_NAME}/tests/integration/test_job.py',
            "python_file_uris": PY_FILES,
        }
    )

    end_pipeline = EmptyOperator(
        task_id='end_production_pipeline'
    )


start_pipeline >> run_unit_tests >> run_integration_tests >> end_pipeline
    
