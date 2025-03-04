# poetry-lambda

Sandbox to try building an [AWS Lambda](https://aws.amazon.com/lambda/) with [Flask](https://pypi.org/project/flask/), [DI](https://pinboard.in/u:brunns/t:dependency-injection) using [wireup](https://pypi.org/project/wireup/), and ~~pynamodb~~ [boto3](https://pypi.org/project/boto3/) to access [Dynamo](https://aws.amazon.com/dynamodb/). 

Local tests will use [localstack](https://www.localstack.cloud/), started & stopped using [pytest-docker](https://pypi.org/project/pytest-docker/).

Requires [poetry](https://python-poetry.org) and [colima](https://github.com/abiosoft/colima). Optionally makes use of [direnv](https://direnv.net/) to set your environment and [xc](https://xcfile.dev/) as a task runner.

## Setup

```sh 
poetry self add poetry-plugin-lambda-build poetry-plugin-export
cp .envrc.template .envrc
direnv allow
xc pc
```

## Tasks

### web

Launch web app locally

Requires: install

```sh
docker compose --file tests/docker-compose.yml up -d
sleep 1

aws dynamodb create-table --table-name People --key-schema '[{"AttributeName": "name", "KeyType": "HASH"}]' --attribute-definitions '[{"AttributeName": "name", "AttributeType": "S"}]' --provisioned-throughput '{"ReadCapacityUnits": 1, "WriteCapacityUnits": 1}' --region eu-west-1 --endpoint-url=http://localhost:4566
aws dynamodb list-tables --region eu-west-1 --endpoint-url=http://localhost:4566

aws dynamodb put-item --table-name People --item '{"name": {"S": "simon"}, "nickname": {"S": "Baldy"}}' --region eu-west-1 --endpoint-url=http://localhost:4566 
aws dynamodb describe-table --table-name People --region eu-west-1 --endpoint-url=http://localhost:4566
aws dynamodb get-item --table-name People --key '{"name": {"S": "simon"}}' --region eu-west-1 --endpoint-url=http://localhost:4566

poetry run web-app

aws dynamodb delete-table --table-name People --region eu-west-1 --endpoint-url=http://localhost:4566
docker compose --file tests/docker-compose.yml down
```

### install

Install dependencies

Run: once

```sh
poetry install
```

### build

Build lambda package in dist/

Requires: colima, install

```
poetry build-lambda -vv
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

Requires: install

```sh
poetry run pytest tests/unit/ --durations=10 --cov-report term-missing --cov src
```

### integration

Integration tests

Requires: colima, install, build

```sh
poetry run pytest tests/integration/ --durations=10 --cov-report term-missing --cov src
```

### format

Format & fix code

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

### colima

Ensure colima is running

Run: once

```shell
colima status || colima start
```

## Initial setup

```shell
poetry new poetry-lambda
cd poetry-lambda
git init
curl https://www.toptal.com/developers/gitignore/api/python,intellij,emacs > .gitignore
poetry add "flask[async]" mangum httpx yarl pydantic wireup pynamodb asgiref boto3 botocore eval-type-backport
poetry add pytest ruff pyhamcrest brunns-matchers factory-boy pytest-asyncio pytest-cov pytest-docker localstack pyright --group dev
poetry self add poetry-plugin-lambda-build poetry-plugin-export
``
