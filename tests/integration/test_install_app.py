import json
import logging
from http import HTTPStatus
from pathlib import Path

import stamina
from botocore.client import BaseClient

logger = logging.getLogger(__name__)


def test_install_and_call_lambda(lambda_client: BaseClient):
    # Given
    function_name = "lambda_function"
    with Path("dist/poetry-lambda.zip").open("rb") as zipfile:
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime="python3.13",
            Role="arn:aws:iam::123456789012:role/test-role",
            Handler="poetry_lambda.lambda_function.lambda_handler",
            Code={"ZipFile": zipfile.read()},
            Timeout=180,
            Environment={
                "Variables": {
                    "ETC_CHANNEL": "dummy_chat@id.007",
                }
            },
        )
    logger.info("loaded zip")
    wait_for_function_active(function_name, lambda_client)
    logger.info("function active")

    # When
    response = lambda_client.invoke(
        FunctionName=function_name, InvocationType="RequestResponse", Payload=json.dumps({})
    )

    # Then
    assert response["StatusCode"] == HTTPStatus.OK
    payload = response["Payload"].read()
    logger.info(payload)


class FunctionNotActiveError(Exception):
    """Function not yet active"""


def wait_for_function_active(function_name, lambda_client):
    for attempt in stamina.retry_context(on=FunctionNotActiveError):
        with attempt:
            logger.info("waiting")
            response = lambda_client.get_function(FunctionName=function_name)
            function_state = response["Configuration"]["State"]
            logger.info("function_state %s", function_state)
            if function_state != "Active":
                raise FunctionNotActiveError
