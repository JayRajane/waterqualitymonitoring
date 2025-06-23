# from airflow import DAG
# from airflow.operators.python import PythonOperator # type: ignore
# from datetime import datetime, timedelta

# def hello_task():
#     print("👋 Hello from Airflow! Running every 1 minute.")

# default_args = {
#     'owner': 'airflow',
#     'retries': 1,
#     'retry_delay': timedelta(seconds=30)
# }

# with DAG(
#     dag_id='hello_every_minute',
#     default_args=default_args,
#     description='Print hello every 1 minute',
#     schedule_interval='*/1 * * * *',
#     start_date=datetime(2024,1,1),
#     catchup=False,
#     tags=['example'],
# ) as dag:
#     task = PythonOperator(
#         task_id='say_hello',
#         python_callable=hello_task
#     ),