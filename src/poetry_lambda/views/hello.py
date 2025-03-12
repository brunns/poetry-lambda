import logging
from http import HTTPStatus

from flask import Blueprint, make_response
from flask.typing import ResponseReturnValue

from poetry_lambda.model.person import Name
from poetry_lambda.services import PersonService
from poetry_lambda.services.person_services import UnknownPersonError
from poetry_lambda.views.response_models import HelloResponse, Problem

logger = logging.getLogger(__name__)

hello = Blueprint("hello", __name__)


@hello.get("/")
@hello.get("/<name>")
def hello_world(person_service: PersonService, name: Name | None = None) -> ResponseReturnValue:
    try:
        nickname = person_service.get_nickname(name)
        hello_response = HelloResponse(status=HTTPStatus.OK, message=f"Hello {nickname}!")
        return hello_response.model_dump()
    except UnknownPersonError:
        problem = Problem(title="Name not found", status=HTTPStatus.NOT_FOUND, detail=f"Name {name} not found.")
        return make_response(problem.model_dump(), HTTPStatus.NOT_FOUND)
