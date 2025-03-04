import logging
from typing import Any

from boto3.resources.base import ServiceResource
from botocore.exceptions import ClientError
from pydantic import ValidationError
from wireup import service

from poetry_lambda.model.person import Person

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


@service
def people_table(dynamodb_resource: ServiceResource) -> Any:
    logger.info("attaching to table People using %s", dynamodb_resource)
    table = dynamodb_resource.Table("People")  # type: ignore[reportAttributeAccessIssue]
    logger.info("got %s", table)
    return table


@service
class PersonRepo:
    def __init__(self, people_table: Any) -> None:
        super().__init__()
        self.people_table = people_table

    def get_nickname(self, name: str) -> str:
        try:
            response = self.people_table.get_item(Key={"name": name})
            person = Person.model_validate(response.get("Item"))
            return person.nickname
        except ClientError as e:
            logger.exception("Person not found with name=%r", name, exc_info=e)
            raise NotFoundError from e
        except ValidationError as e:
            logger.exception("Invalid record for Person with name=%r", name, exc_info=e)
            raise
        else:
            return person.nickname
