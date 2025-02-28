import pytest
from brunns.matchers.werkzeug import is_werkzeug_response
from flask.testing import FlaskClient
from hamcrest import assert_that, contains_string

from poetry_lambda.model.name import Name


@pytest.fixture(autouse=True, scope="module")
def names_table(localstack):  # noqa: ARG001
    if not Name.exists():
        Name.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    n = Name(name="simon", nickname="Baldy")
    n.save()
    yield
    n.delete()


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
