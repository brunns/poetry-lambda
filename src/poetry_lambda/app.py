import wireup.integration.flask
from flask import Flask, jsonify
from flask.typing import ResponseReturnValue

from poetry_lambda import services
from poetry_lambda.services import NameService


def create_app() -> Flask:
    app = Flask(__name__)
    app.logger.info("app created")

    @app.route("/")
    def hello_world(name_service: NameService) -> ResponseReturnValue:
        app.logger.debug("name_service: %s", name_service)
        return jsonify(status=200, message=f"Hello {name_service.get_name()}!")

    container = wireup.create_container(service_modules=[services])
    wireup.integration.flask.setup(container, app, import_flask_config=True)
    app.logger.info("app ready")
    return app


def lambda_handler(event, context):
    from mangum import Mangum

    handler = Mangum(create_app())
    return handler(event, context)


def main() -> None:
    app = create_app()
    app.run(debug=True)


if __name__ == "__main__":
    main()
