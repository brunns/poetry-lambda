import json
import logging
from http import HTTPStatus
from pathlib import Path

import httpx
import stamina
from botocore.client import BaseClient
from brunns.matchers.response import is_response
from hamcrest import assert_that, contains_string, has_entries
from yarl import URL

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
    payload = json.loads(response["Payload"].read().decode("utf-8"))
    assert_that(payload, has_entries(statusCode=HTTPStatus.OK, message=contains_string("Hello")))


def test_install_and_call_lambda_flask(lambda_client: BaseClient):
    # Given
    function_name = "lambda_flask_function"
    with Path("dist/poetry-lambda.zip").open("rb") as zipfile:
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime="python3.13",
            Role="arn:aws:iam::123456789012:role/test-role",
            Handler="poetry_lambda.app.lambda_handler",
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
    request_payload = {
        "version": "2.0",
        "routeKey": "GET /",
        "rawPath": "/",
        "rawQueryString": "",
        "headers": {"accept": "application/json", "content-type": "application/json"},
        "requestContext": {"http": {"sourceIp": "192.0.0.1", "method": "GET", "path": "/", "protocol": "HTTP/1.1"}},
        "body": None,
        "isBase64Encoded": False,
    }
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(request_payload),
    )

    # Then
    assert_that(response, has_entries(StatusCode=HTTPStatus.OK))
    response_payload = json.loads(response["Payload"].read().decode("utf-8"))
    logger.info(response_payload)
    assert_that(response_payload, has_entries(statusCode=HTTPStatus.OK, body=contains_string("Hello")))


def test_install_and_call_flask_lambda_over_http(lambda_client: BaseClient):
    # Given
    function_name = "lambda_flask_function_for_http"
    with Path("dist/poetry-lambda.zip").open("rb") as zipfile:
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime="python3.13",
            Role="arn:aws:iam::123456789012:role/test-role",
            Handler="poetry_lambda.app.lambda_handler",
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

    response = lambda_client.create_function_url_config(FunctionName=function_name, AuthType="NONE")

    function_url = URL(response["FunctionUrl"])
    logger.info("FunctionUrl: %s", function_url)

    # When
    httpx.get(str(function_url))

    # Then
    assert_that(response, is_response().with_status_code(HTTPStatus.OK).and_body(contains_string("Hello")))


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
