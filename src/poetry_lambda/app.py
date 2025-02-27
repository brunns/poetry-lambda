import logging
from typing import Any

import wireup.integration.flask
from flask import Flask, jsonify
from flask.typing import ResponseReturnValue
from mangum import Mangum

from poetry_lambda import services
from poetry_lambda.services import NameService

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def hello_world(name_service: NameService) -> ResponseReturnValue:
        return jsonify(status=200, message=f"Hello {name_service.get_name()}!")

    container = wireup.create_container(service_modules=[services])
    wireup.integration.flask.setup(container, app, import_flask_config=True)
    return app


def lambda_handler(event: dict[str:Any], context: dict[str:Any]) -> dict[str:Any]:
    handler = Mangum(create_app())
    return handler(event, context)


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
