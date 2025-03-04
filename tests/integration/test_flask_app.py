from collections.abc import Generator

import pytest
from brunns.matchers.werkzeug import is_werkzeug_response
from flask.testing import FlaskClient
from hamcrest import assert_that, contains_string

from poetry_lambda.model.person import Person
from tests.utils.builders import PersonFactory


@pytest.fixture(autouse=True, scope="module")
def persisted_person(people_table: type[Person]) -> Generator[Person]:  # noqa: ARG001
    person = PersonFactory()
    person.save()
    yield person
    person.delete()


def test_no_name_given(client: FlaskClient):
    # Given

    # When
    response = client.get("/")

    # Then
    assert_that(response, is_werkzeug_response().with_status_code(200).and_text(contains_string("Hello World")))


def test_app_for_name_with_nickname(client: FlaskClient):
    # Given

    # When
    response = client.get("/simon")

    # Then
    assert_that(response, is_werkzeug_response().with_status_code(200).and_text(contains_string("Hello Baldy")))
