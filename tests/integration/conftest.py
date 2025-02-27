import logging

import boto3
import botocore
import httpx
import pytest
from botocore.client import BaseClient
from httpx import URL, RequestError

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
    return boto3.client(
        "lambda",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
        endpoint_url=str(localstack),
        config=botocore.config.Config(retries={"max_attempts": 0}),
    )
