import logging
from http import HTTPStatus
from typing import Any

import wireup.integration.flask
from asgiref.wsgi import WsgiToAsgi
from flask import Flask
from flask.typing import ResponseReturnValue
from mangum import Mangum
from mangum.types import LambdaContext, LambdaEvent
from pydantic import BaseModel

from poetry_lambda import repos, services
from poetry_lambda.services import NameService

DEBUG = True


class Hello(BaseModel):
    status: int
    message: str


def create_app() -> Flask:
    app = Flask(__name__)
    app.logger.info("app created")
    if DEBUG:
        app.logger.setLevel(logging.DEBUG)

    @app.get("/")
    @app.get("/<name>")
    def hello_world(name_service: NameService, name: str | None = None) -> ResponseReturnValue:
        hello = Hello(status=HTTPStatus.OK, message=f"Hello {name_service.get_nickname(name)}!")
        return hello.model_dump_json()

    container = wireup.create_container(service_modules=[services, repos])
    wireup.integration.flask.setup(container, app, import_flask_config=True)
    app.logger.info("app ready")
    return app


def lambda_handler(event: LambdaEvent, context: LambdaContext) -> dict[str, Any]:
    handler = Mangum(WsgiToAsgi(create_app()))
    return handler(event, context)


def main() -> None:
    app = create_app()
    app.run(debug=DEBUG)


if __name__ == "__main__":
    main()
