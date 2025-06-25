from airflow import DAG
from datetime import datetime, timedelta
from airflow.decorators import task
from airflow_package.src.db.mysql_client import MySQLClient
from typing import Optional, Dict

# def hello_task():
#     print("👋 Hello from Airflow! Running every 1 minute.")

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(seconds=30)
}

with DAG(
    dag_id='hello_every_minute',
    default_args=default_args,
    description='Print hello every 1 minute',
    schedule_interval='*/15 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:

    @task
    def say_hello() -> str:
        msg = "👋 Hello from Airflow!"
        return msg

    @task
    def add_new_str(previous_msg: str) -> str:
        new_msg = f"{previous_msg} | processed new msg"
        return new_msg

    @task
    def store_message(final_msg: str):
        print(f"📦 Storing message: {final_msg}")

    @task
    def fetch_user(messgae: str) -> Optional[Dict]:
        client = MySQLClient()
        return {'messgae': messgae, 'data': client.fetch_user(1)}

    t1 = say_hello()
    t2 = add_new_str(t1)
    t4 = fetch_user(t2)
    t3 = store_message(t4)

    t1 >> t2 >> t4 >> t3
    # task = PythonOperator(
    #     task_id='say_hello',
    #     python_callable=hello_task
    # ),
