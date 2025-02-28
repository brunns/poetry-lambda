# type: ignore
import logging
from typing import Any

import boto3
import botocore

logger = logging.getLogger(__name__)


def lambda_handler(event: dict[str:Any], context: dict[str:Any]) -> dict[str:Any]:  # noqa: ARG001
    logger.info("boto3 version: %s", boto3.__version__)
    logger.info("botocore version: %s", botocore.__version__)

    return {"statusCode": 200, "message": "Hello World!"}
