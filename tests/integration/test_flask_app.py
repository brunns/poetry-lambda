from collections.abc import Generator
from typing import Any

import pytest
from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from flask.testing import FlaskClient
from hamcrest import assert_that, contains_string

from poetry_lambda.model.person import Person
from tests.utils.builders import PersonFactory


@pytest.fixture(autouse=True, scope="module")
def persisted_person(people_table: Any) -> Generator[Person]:
    person = PersonFactory()
    people_table.put_item(Item=person.model_dump())
    yield person
    people_table.delete_item(Key={"name": person.name})


def test_no_name_given(client: FlaskClient):
    """Given dynamodb running in localstack, hit the endpoint via http"""
    # Given

    # When
    response = client.get("/")

    # Then
    assert_that(response, is_response().with_status_code(200).and_text(contains_string("Hello World")))


def test_app_for_name_with_nickname(client: FlaskClient):
    # Given

    # When
    response = client.get("/simon")

    # Then
    assert_that(response, is_response().with_status_code(200).and_text(contains_string("Hello Baldy")))


def test_app_for_nonexistent_name(client: FlaskClient):
    # Given

    # When
    response = client.get("/fred")

    # Then
    assert_that(response, is_response().with_status_code(404))
