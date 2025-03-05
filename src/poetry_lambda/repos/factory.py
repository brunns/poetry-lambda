import logging
import os
from typing import Annotated

import boto3
from boto3.resources.base import ServiceResource
from botocore.client import BaseClient
from wireup import Inject, service
from yarl import URL

logger = logging.getLogger(__name__)


@service
def dynamodb_resource_factory(
    dynamodb_endpoint: Annotated[URL, Inject(param="dynamodb_endpoint")],
    aws_region: Annotated[str, Inject(param="aws_region")],
) -> ServiceResource:
    logger.info("creating dynamodb_resource with endpoint %s, region %s", dynamodb_endpoint, aws_region)
    resource = boto3.resource(
        "dynamodb",
        endpoint_url=str(dynamodb_endpoint),
        region_name=aws_region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY", "fake"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "fake"),
    )
    logger.info("returning %r", resource)
    return resource


@service
def dynamodb_client_factory(
    dynamodb_endpoint: Annotated[URL, Inject(param="dynamodb_endpoint")],
    aws_region: Annotated[str, Inject(param="aws_region")],
) -> BaseClient:
    logger.info("creating dynamodb_client with endpoint %s, region %s", dynamodb_endpoint, aws_region)
    return boto3.client(
        "dynamodb",
        endpoint_url=str(dynamodb_endpoint),
        region_name=aws_region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY", "fake"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "fake"),
    )
