import json
import logging
from collections.abc import Generator
from http import HTTPStatus
from typing import Any

import httpx
import pytest
from botocore.client import BaseClient
from brunns.matchers.response import is_response
from hamcrest import assert_that, contains_string, has_entries
from yarl import URL

from poetry_lambda.model.person import Person
from tests.utils.builders import PersonFactory

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True, scope="module")
def persisted_person(people_table: Any) -> Generator[Person]:
    person = PersonFactory(name="fred", nickname="Freddy")

    people_table.put_item(Item=person.model_dump())
    yield person
    people_table.delete_item(Key={"name": person.name})


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


@pytest.mark.xfail
def test_install_and_call_flask_lambda_with_nickname_over_http(flask_function_url: URL):
    # Given

    # When
    response = httpx.get(str(flask_function_url / "fred"))

    # Then
    assert_that(response, is_response().with_status_code(HTTPStatus.OK).and_body(contains_string("Freddy")))
