import logging
import os
import traceback
from http import HTTPStatus
from typing import Any

import wireup.integration.flask
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, make_response
from flask.typing import ResponseReturnValue
from mangum import Mangum
from mangum.types import LambdaContext, LambdaEvent
from yarl import URL

from poetry_lambda import repos, services
from poetry_lambda.log_config import LOG_LEVEL, init_logging
from poetry_lambda.response_models import HelloResponse, Problem
from poetry_lambda.services import PersonService
from poetry_lambda.services.person_services import UnknownPersonError


def create_app() -> Flask:
    init_logging()

    app = Flask(__name__)
    app.logger.info("app created")

    @app.get("/")
    @app.get("/<name>")
    def hello_world(person_service: PersonService, name: str | None = None) -> ResponseReturnValue:
        try:
            hello = HelloResponse(status=HTTPStatus.OK, message=f"Hello {person_service.get_nickname(name)}!")
            return hello.model_dump()
        except UnknownPersonError:
            problem = Problem(title="Name not found", status=HTTPStatus.NOT_FOUND, detail=f"Name {name} not found.")
            return make_response(problem.model_dump(), HTTPStatus.NOT_FOUND)
        except Exception as e:
            app.logger.exception("Unexpected Exception", exc_info=e)
            problem = Problem(
                title="Unexpected Exception",
                type=str(type(e)),
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="".join(traceback.format_exception(e)),
            )
            return make_response(problem.model_dump(), HTTPStatus.INTERNAL_SERVER_ERROR)

    config = {
        "dynamodb_endpoint": URL(os.getenv("DYNAMODB_ENDPOINT", "http://localhost:4566")),
        "aws_region": os.getenv("AWS_REGION", "eu-west-1"),
    }
    app.logger.info("config: %s", config)
    container = wireup.create_container(service_modules=[services, repos], parameters=config)
    wireup.integration.flask.setup(container, app, import_flask_config=True)
    app.logger.info("app ready")
    return app


def lambda_handler(event: LambdaEvent, context: LambdaContext) -> dict[str, Any]:
    handler = Mangum(WsgiToAsgi(create_app()))
    return handler(event, context)


def main() -> None:
    app = create_app()
    app.run(debug=LOG_LEVEL == logging.DEBUG)


if __name__ == "__main__":
    main()
