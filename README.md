# poetry-lambda

Snadbox to try building an AWS Lambda with Flask, DI using wireup, and pynamodb to access Dynamo. 

Local tests should use localstack, started & stopped using pytest-docker.

## Tasks

### web

Launch web app locally

```sh
poetry run web-app
```

### pc

Precommit tasks

Requires: test, lint

```python
#!/usr/bin/env python
import this
```

### test

All tests

Requires: unit, integration

### unit

Unit tests

```sh
poetry run pytest tests/unit/ --durations=10 --cov-report term-missing --cov src
```

### integration

Integration tests

```sh
colima status || colima start
poetry run pytest tests/integration/ --durations=10 --cov-report term-missing --cov src
```

### format

Format code

```sh 
poetry run ruff format .
poetry run ruff check . --fix-only
```

### lint

Lint code

```sh 
poetry run ruff format . --check
poetry run ruff check .
poetry run pyright
```

## Initial setup

```shell
poetry new poetry-lambda
cd poetry-lambda
git init
curl https://www.toptal.com/developers/gitignore/api/python,intellij,emacs > .gitignore
poetry add "flask[async]" httpx yarl poetry-plugin-lambda-build poetry-plugin-export pydantic wireup pynamodb
poetry add pytest ruff pyhamcrest brunns-matchers factory-boy pytest-asyncio pytest-cov pytest-docker localstack pyright --group dev
``