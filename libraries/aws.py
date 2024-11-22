import os
import boto3
from io import BytesIO
from pathlib import Path
from typing import Union, Any
from datetime import timedelta
from ..dags.includes.settings import settings
from ..utils.helper_functions import generate_random_file_name
from dotenv import load_dotenv
from boto3.s3.transfer import TransferConfig

load_dotenv()

# Load environment variables


session = boto3.Session(
    aws_access_key_id=settings.AWS.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS.AWS_REGION,
)

S3_RESOURCE = session.resource('s3')
S3_CLIENT = session.client('s3')


## List all buckets
def upload_file_to_S3_V1(
    file: Union[BytesIO, bytes, Any],
    mime_type: str,
    folder: Union[str, None] = None,
    Key: Union[str, None] = None,
) -> Union[str, None]:
    try:
        bucket = S3_RESOURCE.Bucket(settings.AWS.AWS_S3_BUCKET_NAME)

        if Key is None:
            Key = generate_random_file_name()

        environment = "development" if settings.DEBUG else "production"

        final_key_name = Key if folder is None else f"{environment}/{folder}/{Key}"

        if isinstance(file, bytes):
            file = BytesIO(file)

        bucket.upload_fileobj(file, final_key_name, ExtraArgs={'ContentType': mime_type})

        return final_key_name

    except Exception as e:
        # // Use Sentry to capture error
        print(e)
        return None


# Use V2 Upload for large file upload
def upload_file_to_S3_V2(
    file,
    Key: str,
    mime_type: str = None,
    multipart_threshold: int = 8,
    max_concurrency: int = 10,
    multipart_chunksize: int = 8,
    use_threads: bool = True,
) -> None:

    try:
        bucket = S3_RESOURCE.Bucket(settings.AWS.AWS_S3_BUCKET_NAME)

        bucket.upload_fileobj(file, Key, ExtraArgs={'ContentType': mime_type})

        # Set up TransferConfig to control multipart upload settings, (For large files upload)
        config = TransferConfig(
            # 8 MB threshold
            multipart_threshold=multipart_threshold * 1024 * 1024,
            # Number of concurrent threads
            max_concurrency=max_concurrency,
            # 8 MB chunks
            multipart_chunksize=multipart_chunksize * 1024 * 1024,
            use_threads=use_threads,
        )

        bucket.upload_fileobj(file, Key, ExtraArgs={'ContentType': mime_type}, Config=config)

    except Exception as e:
        # // Use Sentry to capture error
        print(e)
        return None


def get_all_objects_from_S3_V1():
    try:
        bucket = S3_RESOURCE.Bucket(settings.AWS.AWS_S3_BUCKET_NAME)
        return bucket.objects.all()

    except Exception as e:
        # // Use Sentry to capture error
        print(e)
        return None


def download_file_from_S3_V1(Key: str, filename: str | Path, file_extension: str) -> None:
    try:
        bucket = S3_RESOURCE.Bucket(settings.AWS.AWS_S3_BUCKET_NAME)
        bucket.download_file(Key=Key, Filename=f"{filename}.{file_extension}")

    except Exception as e:
        # // Use Sentry to capture error
        print(e)
        return None


def get_signed_url_from_S3(Key: str, expires_in: timedelta | float = timedelta(days=1).total_seconds()):
    try:
        presigned_url = S3_CLIENT.generate_presigned_url(
            'get_object', Params={'Bucket': settings.AWS.AWS_S3_BUCKET_NAME, 'Key': Key}, ExpiresIn=expires_in
        )

        return presigned_url

    except Exception as e:
        # // Use Sentry to capture error
        print(e)
        return None


def delete_file_from_S3_V1(Key: str):
    try:
        bucket = S3_RESOURCE.Bucket(settings.AWS.AWS_S3_BUCKET_NAME)

        bucket.Object(Key).delete()

    except Exception as e:
        # // Use Sentry to capture error
        print(e)
        return None
