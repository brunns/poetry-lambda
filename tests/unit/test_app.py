import logging

from brunns.matchers.werkzeug import is_werkzeug_response
from flask import Flask
from flask.testing import FlaskClient
from hamcrest import assert_that, contains_string
from wireup.integration.flask import get_container

from poetry_lambda.services import NameService

logger = logging.getLogger(__name__)


class FakeNameService(NameService):
    def __init__(self):
        pass

    def get_nickname(self, name: str | None = None) -> str:
        return name.upper() if name else "Default"


def test_name_given(app: Flask, client: FlaskClient):
    with get_container(app).override.service(NameService, new=FakeNameService()):
        response = client.get("/simon")
        assert_that(response, is_werkzeug_response().with_status_code(200).and_text(contains_string("SIMON")))


def test_default_name(app: Flask, client: FlaskClient):
    with get_container(app).override.service(NameService, new=FakeNameService()):
        response = client.get("/")
        assert_that(response, is_werkzeug_response().with_status_code(200).and_text(contains_string("Default")))
