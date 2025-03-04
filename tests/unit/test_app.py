import logging
from http import HTTPStatus

from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from flask import Flask
from flask.testing import FlaskClient
from hamcrest import assert_that, contains_string
from wireup.integration.flask import get_container

from poetry_lambda.services import PersonService
from poetry_lambda.services.person_services import UnknownPersonError

logger = logging.getLogger(__name__)


class FakePersonService(PersonService):
    def __init__(self):
        pass

    def get_nickname(self, name: str | None = None) -> str:
        return name.upper() if name else "Default"


class FakeUnknownPersonService(PersonService):
    def __init__(self):
        pass

    def get_nickname(self, _: str | None = None) -> str:
        raise UnknownPersonError


def test_name_given(app: Flask, client: FlaskClient):
    with get_container(app).override.service(PersonService, new=FakePersonService()):
        response = client.get("/simon")
        assert_that(response, is_response().with_status_code(HTTPStatus.OK).and_text(contains_string("SIMON")))


def test_default_name(app: Flask, client: FlaskClient):
    with get_container(app).override.service(PersonService, new=FakePersonService()):
        response = client.get("/")
        assert_that(response, is_response().with_status_code(HTTPStatus.OK).and_text(contains_string("Default")))


def test_unknown_name(app: Flask, client: FlaskClient):
    with get_container(app).override.service(PersonService, new=FakeUnknownPersonService()):
        response = client.get("/fred")
        assert_that(response, is_response().with_status_code(HTTPStatus.NOT_FOUND))
