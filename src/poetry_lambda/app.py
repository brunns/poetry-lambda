import logging
import os
from typing import Any

import wireup.integration.flask
from asgiref.wsgi import WsgiToAsgi
from flask import Flask
from mangum import Mangum
from mangum.types import LambdaContext, LambdaEvent
from yarl import URL

from poetry_lambda import repos, services
from poetry_lambda.log_config import LOG_LEVEL, init_logging
from poetry_lambda.views.hello import hello


def create_app() -> Flask:
    init_logging()

    app = Flask(__name__)
    app.logger.info("app created")

    app.register_blueprint(hello)

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
