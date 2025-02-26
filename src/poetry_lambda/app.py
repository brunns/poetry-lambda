import wireup.integration.flask
from flask import Flask
from flask.typing import ResponseReturnValue

from poetry_lambda import services
from poetry_lambda.services import NameService

app = Flask(__name__)


@app.route("/")
def hello_world(name_service: NameService) -> ResponseReturnValue:
    return f"<p>Hello, {name_service.get_name()}!</p>"


container = wireup.create_container(service_modules=[services])
wireup.integration.flask.setup(container, app, import_flask_config=True)


def main() -> None:
    app.run(debug=True)  # noqa: S201


if __name__ == "__main__":
    main()
