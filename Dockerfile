ARG PYTHON_VERSION=3.9.1
FROM python:${PYTHON_VERSION}-alpine as base

FROM apache/airflow:2.10.3

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python dependencies
RUN pip install --no-cache-dir scikit-learn pandas numpy python-dotenv boto3 pydantic pydantic-settings

