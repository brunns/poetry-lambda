import json
import logging
from http import HTTPStatus

import httpx
from botocore.client import BaseClient
from brunns.matchers.response import is_response
from hamcrest import assert_that, contains_string, has_entries
from yarl import URL

logger = logging.getLogger(__name__)


def test_install_and_call_lambda(lambda_client: BaseClient, lambda_function: str):
    # Given

    # When
    response = lambda_client.invoke(
        FunctionName=lambda_function, InvocationType="RequestResponse", Payload=json.dumps({})
    )

    # Then
    assert response["StatusCode"] == HTTPStatus.OK
    payload = json.loads(response["Payload"].read().decode("utf-8"))
    assert_that(payload, has_entries(statusCode=HTTPStatus.OK, message=contains_string("Hello")))


def test_install_and_call_lambda_flask(lambda_client: BaseClient, flask_function: str):
    # Given

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
        FunctionName=flask_function,
        InvocationType="RequestResponse",
        Payload=json.dumps(request_payload),
    )

    # Then
    assert_that(response, has_entries(StatusCode=HTTPStatus.OK))
    response_payload = json.loads(response["Payload"].read().decode("utf-8"))
    logger.info(response_payload)
    assert_that(response_payload, has_entries(statusCode=HTTPStatus.OK, body=contains_string("Hello")))


def test_install_and_call_flask_lambda_over_http(flask_function_url: URL):
    # Given

    # When
    response = httpx.get(str(flask_function_url))

    # Then
    assert_that(response, is_response().with_status_code(HTTPStatus.OK).and_body(contains_string("Hello")))
