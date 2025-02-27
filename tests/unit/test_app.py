import logging

from brunns.matchers.werkzeug import is_werkzeug_response
from hamcrest import assert_that, contains_string
from wireup.integration.flask import get_container

from poetry_lambda.services import NameService

logger = logging.getLogger(__name__)


def test_app(app, client):
    class FakeNameService(NameService):
        def get_name(self) -> str:
            return "Test Value"

    with get_container(app).override.service(NameService, new=FakeNameService()):
        response = client.get("/")
        assert_that(response, is_werkzeug_response().with_status_code(200).and_text(contains_string("Test Value")))
