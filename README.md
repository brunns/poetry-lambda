# poetry-lambda

Sandbox to try building an [AWS Lambda](https://aws.amazon.com/lambda/) with [Flask](https://pypi.org/project/flask/), and ~~pynamodb~~ [boto3](https://pypi.org/project/boto3/) to access [Dynamo](https://aws.amazon.com/dynamodb/). 

We'll be separating our [presentation](https://martinfowler.com/eaaDev/SeparatedPresentation.html) layer (where API logic lives), [business services](https://martinfowler.com/eaaCatalog/serviceLayer.html) layer (where business logic lives) and [repository](https://martinfowler.com/eaaCatalog/repository.html) layer (where database logic lives). We will be using [wireup](https://pypi.org/project/wireup/) for [dependency injection](https://pinboard.in/u:brunns/t:dependency-injection), so services get their dependencies given to them ("injection"), and wireup takes care of that. We'll be using [Pydantic](https://pypi.org/project/pydantic/) for both response models and database models.

Local tests will use [localstack](https://www.localstack.cloud/), started & stopped using [pytest-docker](https://pypi.org/project/pytest-docker/). We'll make extensive use of [pytest fixtures](https://docs.pytest.org/en/6.2.x/fixture.html), [builders](https://pypi.org/project/factory-boy/) and [matchers](https://pypi.org/project/pyhamcrest/) to keep our tests clean.

Requires [Python](https://www.python.org/) version 3.13 (I use [pyenv](https://github.com/pyenv/pyenv) for Python versions) and [poetry](https://python-poetry.org) version 2. Optionally makes use of [direnv](https://direnv.net/) to set your environment and [xc](https://xcfile.dev/) as a task runner.

## Setup

### Mac

On a Mac, [colima](https://github.com/abiosoft/colima) is required. I needed these steps:

```sh 
poetry self add poetry-plugin-lambda-build poetry-plugin-export
cp .envrc.template .envrc
direnv allow
xc pc
```

### Linux

Ubuntu Linux / WSL

These are the steps that have worked for me
(not sure if they are the best practice, but here we are).

#### Install Python 3.13

```sh
apt update
add-apt-repository ppa:deadsnakes/ppa
apt install python3.13 python3.13-venv python3.13-dev
```

#### Install Poetry

```sh
  curl -sSL https://install.python-poetry.org | python3 -
  poetry --version
```
  Note; install via the package manager did NOT work for me due to version problems (apt install python3-poetry)

#### Install xc

```sh
 curl -fsSL "https://github.com/joerdav/xc/releases/download/v0.8.0/xc_0.8.0_linux_amd64" -o /usr/local/bin/xc
 chmod +x /usr/local/bin/xc
```

#### Install docker compose (different from docker-compose)

```
  DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
  mkdir -p $DOCKER_CONFIG/cli-plugins
  curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
  chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
  docker compose --version
```

At this point, should be ready to start with the git repo specific setup.
First, set your poetry

```sh
poetry env use python3.13
source $(poetry env info --path)/bin/activate
```

```sh
poetry self add poetry-plugin-lambda-build poetry-plugin-export
xc pc
```

If you get there with minimal scars, well done.
You can try the following

#### Run the web app

`xc web`
Navigate to url in your browser http://127.0.0.1:5000
and you should see `{"message": "Hello World!","status": 200}`

Also navigate to http://127.0.0.1:5000/simon 
to check the dynamoDB connection. You should see `{"message": "Hello Baldy!","status": 200}`


#### Test the unit and integration tests

`xc test`

(currently integration test failing on Linux, 
might need to add some setup or additional info to the above to get working)

#### Before committing

Run all tests and linting

`xc pc` 

### Windows

TODO

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

Requires: docker, install

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

```sh
poetry run coverage report
```

### unit

Unit tests

Requires: install

```sh
poetry run pytest tests/unit/ --durations=10 --cov-report= --cov src/poetry_lambda
```

### integration

Integration tests

Requires: docker, install, build

```sh
poetry run pytest tests/integration/ --durations=10 --cov-append --cov-report= --cov src/poetry_lambda
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

### docker

Ensure docker is running

Run: once

```sh
unamestr=$(uname)
if [[ "$unamestr" == 'Linux' ]]; then
  docker status || docker start
elif [[ "$unamestr" == 'Darwin' ]]; then
  colima status || colima start
else
  echo "Unknown Platform"
fi
```

## Initial setup

The steps I took to create this spike repo:

```shell
poetry new poetry-lambda
cd poetry-lambda
git init
curl https://www.toptal.com/developers/gitignore/api/python,intellij,emacs > .gitignore
poetry add "flask[async]" mangum httpx yarl pydantic wireup pynamodb boto3 botocore eval-type-backport
poetry add pytest ruff pyhamcrest brunns-matchers factory-boy pytest-asyncio pytest-cov pytest-docker localstack pyright --group dev
poetry self add poetry-plugin-lambda-build poetry-plugin-export
```
