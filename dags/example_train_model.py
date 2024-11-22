import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from includes.libraries.aws import upload_file_to_S3_V1
import numpy as np
import pickle


def create_dataset(**kwargs):
    X, y = make_classification(
        n_samples=1000,   # Number of samples
        n_features=20,    # Number of features
        n_informative=2,  # Number of informative features
        n_redundant=10,   # Number of redundant features
        n_classes=2,      # Number of classes (binary classification)
        random_state=42   # For reproducibility
    )


    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    temp_dir = "./temp"

    os.makedirs(temp_dir, exist_ok=True)

    with open(f'{temp_dir}/train_data.pkl', 'wb') as f:
        pickle.dump((x_train, y_train), f)

    with open(f'{temp_dir}/test_data.pkl', 'wb') as f:
        pickle.dump((x_test, y_test), f)

    print("X and Y features baby!")

    kwargs['ti'].xcom_push(key='train_data_path', value=f'{temp_dir}/train_data.pkl')
    kwargs['ti'].xcom_push(key='test_data_path', value=f'{temp_dir}/test_data.pkl')


def transform_data(**kwargs):

    '''
    This function will transform the data, scaling, encoding, etc
    '''

    pass

def train_model(**kwargs):
    train_data_path = kwargs['ti'].xcom_pull(key='train_data_path')

    with open(train_data_path, 'rb') as f:

        x_train, y_train = pickle.load(f)

    model = LogisticRegression()
    model.fit(x_train, y_train)

    temp_dir = "./temp"
    model_path = f'{temp_dir}/model.pkl'

    with open(model_path, "wb") as f:
        pickle.dump(model, f)
        f.close()


    print(model)

    kwargs['ti'].xcom_push(key='model_path', value=model_path)

    print("Model trained and saved!")


dag = DAG(
    'example_train_model',
    description='Example Train Model DAG',
    default_args={
        'start_date': days_ago(1),
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    },
    schedule_interval='* * * * *',
    tags=['Example Train Model Dag'],
    catchup=False
)

create_data_for_pipeline = PythonOperator(
    task_id='create_dataset',
    python_callable=create_dataset,
    dag=dag
)

train_model_pipeline = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag
)

send_completion_email = EmailOperator(
    task_id="send_completion_email__example_train_model",
    to=["wisdomdakoh@gmail.com"],
    subject="Task for example train model completed",
    html_content="Yep its done boss",
)




create_data_for_pipeline >> train_model_pipeline >> send_completion_email

# from airflow.models import Variable

# # Get a variable value
# api_key = Variable.get("api_key")

# # Get a variable with a default value if it does not exist
# api_key = Variable.get("api_key", default_var="default_value")