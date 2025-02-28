import pytest
from flask import Flask
from flask.testing import FlaskClient

from poetry_lambda.app import create_app


@pytest.fixture
def app() -> Flask:
    return create_app()


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()
