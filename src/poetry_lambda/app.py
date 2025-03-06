import logging
from typing import Any

import wireup.integration.flask
from asgiref.wsgi import WsgiToAsgi
from flask import Flask
from mangum import Mangum
from mangum.types import LambdaContext, LambdaEvent

from poetry_lambda import repos, services
from poetry_lambda.config import LOG_LEVEL, config, init_logging
from poetry_lambda.views.hello import hello


def create_app() -> Flask:
    init_logging()

    app = Flask(__name__)
    app.logger.info("app created")

    # Register views
    app.register_blueprint(hello)

    # Set up dependency injection using wireup
    container = wireup.create_container(service_modules=[services, repos], parameters=config())
    wireup.integration.flask.setup(container, app, import_flask_config=True)

    app.logger.info("app ready")
    return app


def lambda_handler(event: LambdaEvent, context: LambdaContext) -> dict[str, Any]:
    """For running the Flask app as an AWS Lambda."""
    handler = Mangum(WsgiToAsgi(create_app()))
    return handler(event, context)


def main() -> None:
    """For running the Flask app as a local process."""
    app = create_app()
    app.run(debug=LOG_LEVEL == logging.DEBUG)


if __name__ == "__main__":
    main()
