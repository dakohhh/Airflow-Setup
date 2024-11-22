from io import BytesIO
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from includes.settings import settings
from includes.libraries.aws import upload_file_to_S3_V2, get_object_from_S3_V1


def upload_data(**kwargs):

    text = "Hello, this is a sample text! now its been replace bitch"

    # Convert text to bytes
    text_bytes = text.encode("utf-8")

    # Create a BytesIO object from the bytes
    bytes_io_text = BytesIO(text_bytes)

    key = "airflow_setup_data.pkl"
    
    # Upload data to S3
    final_key_name = upload_file_to_S3_V2(
        file=bytes_io_text,
        Key=key,
        folder='model',
        mime_type="application/octet-stream"
    )


def get_data(**kwargs):

    Key =  "development/model/airflow_setup_data.pkl"

    obj = get_object_from_S3_V1(Key)

    streaming_body = obj.get()['Body']

    content = streaming_body.read()

    print(content)


dag = DAG(
    'use_s3_dag',
    description='Welcome DAG',
    default_args={
        'start_date': days_ago(1),
        'retries': 1,
    },
    tags=['S3 Dag'],
    catchup=False,
    schedule_interval=None,

)



upload_data_pipeline = PythonOperator(
    task_id='upload_data',
    python_callable=upload_data,
    dag=dag
)

get_data_pipeline = PythonOperator(
    task_id='get_data',
    python_callable=get_data,
    dag=dag
)

upload_data_pipeline >> get_data_pipeline