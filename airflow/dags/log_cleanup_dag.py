from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG(
    dag_id="airflow_log_cleanup",
    description="Delete old logs file older than 2 minutes",
    start_date=datetime(2024,1,1),
    schedule_interval='*/2 * * * *',
    catchup=False,
    tags=['housekeeping'],
    default_args={
        'owner': 'airflow',
        'retries': 0
    }
) as dag:
    cleanup_logs = BashOperator(
        task_id='cleanup_old_logs',
        bash_command="""
            echo "🧹 Cleaning logs older than 2 minutes from: {{ var.value.airflow_log_path }}"
            find {{ var.value.airflow_log_path }} -depth -mindepth 1 -mmin +2 -print -delete
        """
    )