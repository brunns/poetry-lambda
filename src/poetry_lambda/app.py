import logging

import wireup.integration.flask
from flask.typing import ResponseReturnValue
from mangum import Mangum
from mangum.types import LambdaContext, LambdaEvent
from quart import Quart, jsonify

from poetry_lambda import services
from poetry_lambda.services import NameService

DEBUG = True


def create_app() -> Quart:
    app = Quart(__name__)
    app.logger.info("app created")
    if DEBUG:
        app.logger.setLevel(logging.DEBUG)

    @app.route("/")
    def hello_world(name_service: NameService) -> ResponseReturnValue:
        app.logger.debug("name_service: %s", name_service)
        return jsonify(status=200, message=f"Hello {name_service.get_name()}!")

    container = wireup.create_container(service_modules=[services])
    wireup.integration.flask.setup(container, app, import_flask_config=True)  # type: ignore
    app.logger.info("app ready")
    return app


def lambda_handler(event: LambdaEvent, context: LambdaContext) -> Mangum:
    handler = Mangum(create_app())  # type: ignore
    return handler(event, context)  # type: ignore


def main() -> None:
    app = create_app()
    app.run(debug=DEBUG)


if __name__ == "__main__":
    main()
