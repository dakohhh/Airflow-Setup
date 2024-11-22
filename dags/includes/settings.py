import os
import certifi
from enum import Enum
from typing import Union
from pathlib import Path
from pydantic import Field
from datetime import timedelta
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


PYTHON_ENV = os.getenv("PYTHON_ENV")

BASE_DIR = Path(__file__).resolve().parent.parent

CERTIFICATE = os.path.join(os.path.dirname(certifi.__file__), "cacert.pem")

# Path to .env file
DOTENV = os.path.join(BASE_DIR, ".env")


class Environment(str, Enum):
    """
    Environment types
    """

    DEVELOPMENT = "development"
    PRODUCTION = "production"


class APIDocsConfig(BaseSettings):
    """
    API Docs configurations
    """

    API_DOCS_USERNAME: Union[str, None] = Field(None, env="API_DOCS_USERNAME")
    API_DOCS_PASSWORD: Union[str, None] = Field(None, env="API_DOCS_PASSWORD")
    API_DOCS_URL: Union[str, None] = Field(None, env="API_DOCS_URL")
    API_REDOC_URL: Union[str, None] = Field(None, env="API_REDOC_URL")
    OPENAPI_URL: Union[str, None] = Field(None, env="OPENAPI_URL")


class AWSConfig(BaseSettings):
    """
    AWS configurations
    """

    AWS_REGION: str = Field(None, env="AWS_REGION")
    AWS_S3_BUCKET_NAME: str = Field(..., env="AWS_S3_BUCKET_NAME")
    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")


class GlobalConfig(BaseSettings):
    """
    Global configurations that are the same across all environments
    """

    APP_NAME: str = Field("REVO Implementation", env="APP_NAME")
    APP_VERSION: str = Field("1.0", env="APP_VERSION")
    APPLICATION_CERTIFICATE: str = Field(default=CERTIFICATE)
    BASE_DIR: Path = Field(default=BASE_DIR)

    # API Docs Configs
    API_DOCS: APIDocsConfig = Field(default_factory=APIDocsConfig)


    AWS: AWSConfig = Field(default_factory=AWSConfig)


class DevelopmentConfig(GlobalConfig):
    """
    Development configurations
    """

    DEBUG: bool = True


class ProductionConfig(GlobalConfig):
    """
    Production configurations
    """

    DEBUG: bool = False


def getenv():

    print(PYTHON_ENV)

    if PYTHON_ENV is None or PYTHON_ENV not in ["development", "production"]:
        raise ValueError("Invalid deployment environment")

    if PYTHON_ENV == "development":
        return DevelopmentConfig()

    return ProductionConfig()


settings = getenv()

# Uncomment the line below to check the settings set
# print(settings)
