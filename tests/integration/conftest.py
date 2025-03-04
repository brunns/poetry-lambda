import logging
from collections.abc import Generator
from pathlib import Path

import boto3
import httpx
import pytest
import stamina
from botocore.client import BaseClient
from httpx import RequestError
from yarl import URL

from poetry_lambda.model.person import Person

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def localstack(docker_ip, docker_services) -> URL:
    logger.info("Starting localstack")
    port = docker_services.port_for("localstack", 4566)
    url = URL(f"http://{docker_ip}:{port}")
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_responsive(url))
    logger.info("localstack running on %s", url)
    return url


def is_responsive(url: URL) -> bool:
    try:
        response = httpx.get(str(url))
        response.raise_for_status()
    except RequestError:
        return False
    else:
        return True


@pytest.fixture(scope="session")
def lambda_client(localstack: URL) -> BaseClient:
    return boto3.client("lambda", endpoint_url=str(localstack))


@pytest.fixture(scope="session")
def dynamodb_client(localstack: URL) -> BaseClient:
    return boto3.client("dynamodb", endpoint_url=str(localstack))


@pytest.fixture(scope="session")
def flask_function(lambda_client: BaseClient) -> str:
    function_name = "flask_function"
    with Path("dist/poetry-lambda.zip").open("rb") as zipfile:
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime="python3.13",
            Role="arn:aws:iam::123456789012:role/test-role",
            Handler="poetry_lambda.app.lambda_handler",
            Code={"ZipFile": zipfile.read()},
            Architectures=["x86_64"],
            Timeout=180,
            Environment={
                "Variables": {
                    "DYNAMODB_ENDPOINT": "http://host.docker.internal:4569",
                }
            },
        )
    logger.info("loaded zip")
    wait_for_function_active(function_name, lambda_client)
    logger.info("function active")
    return function_name


@pytest.fixture(scope="session")
def flask_function_url(lambda_client: BaseClient, flask_function: str) -> URL:
    response = lambda_client.create_function_url_config(FunctionName=flask_function, AuthType="NONE")
    return URL(response["FunctionUrl"])


class FunctionNotActiveError(Exception):
    """Lambda Function not yet active"""


def wait_for_function_active(function_name, lambda_client):
    for attempt in stamina.retry_context(on=FunctionNotActiveError):
        with attempt:
            logger.info("waiting")
            response = lambda_client.get_function(FunctionName=function_name)
            function_state = response["Configuration"]["State"]
            logger.info("function_state %s", function_state)
            if function_state != "Active":
                raise FunctionNotActiveError


@pytest.fixture(scope="session")
def people_table(localstack) -> Generator[type[Person]]:  # noqa: ARG001
    if not Person.exists():
        Person.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    yield Person
    Person.delete_table()
