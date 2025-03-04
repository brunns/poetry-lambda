from typing import Annotated

import boto3
from boto3.resources.base import ServiceResource
from wireup import Inject, service
from yarl import URL


@service
def dynamodb_resource_factory(dynamodb_endpoint: Annotated[URL, Inject(param="dynamodb_endpoint")]) -> ServiceResource:
    return boto3.resource("dynamodb", endpoint_url=str(dynamodb_endpoint))
