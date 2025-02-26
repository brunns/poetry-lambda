import pytest
from flask import Flask
from flask.testing import FlaskClient

from poetry_lambda.app import app as the_app


@pytest.fixture
def app() -> Flask:
    return the_app


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()
