from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.utils.dates import days_ago
import requests
import logging

def print_welcome():
    print("Welcome to the Airflow Tutorial!")


def print_date():
    print(f"Today's date is {datetime.today().date()}")


def print_random_quote():
    try:
        response = requests.get("http://api.quotable.io/random", verify=False)  # or verify=False temporarily
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        data = response.json()
        print(f"Random quote: {data['content']}")
    except requests.exceptions.SSLError as ssl_error:
        logging.error(f"SSL error: {ssl_error}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")


dag = DAG(
    'welcome_dags',
    description='Welcome DAG',
    default_args={
        'start_date': days_ago(1)
    },
    schedule_interval='@daily',
    tags=['First Dag'],
    catchup=False
)

print_welcome_task = PythonOperator(
    task_id='print_welcome',
    python_callable=print_welcome,
    dag=dag
)

print_date_task = PythonOperator(
    task_id='print_date',
    python_callable=print_date,
    dag=dag
)

print_random_quote_task = PythonOperator(
    task_id='print_random_quote',
    python_callable=print_random_quote,
    dag=dag
)

print_welcome_task >> print_date_task >> print_random_quote_task
