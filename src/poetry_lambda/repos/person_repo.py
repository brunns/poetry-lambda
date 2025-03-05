import logging
from typing import Any

from boto3.resources.base import ServiceResource
from botocore.exceptions import ClientError
from pydantic import ValidationError
from wireup import service

from poetry_lambda.model.person import Person
from poetry_lambda.repos.exceptions import NotFoundError

logger = logging.getLogger(__name__)


@service
def people_table(dynamodb_resource: ServiceResource) -> Any:
    logger.info("attaching to table People using %r", dynamodb_resource)
    table = dynamodb_resource.Table("People")  # type: ignore[reportAttributeAccessIssue]
    logger.info("returning %r", table)
    return table


@service
class PersonRepo:
    def __init__(self, people_table: Any) -> None:
        super().__init__()
        logger.info("given %r", people_table)
        self.people_table = people_table

    def get_person(self, name: str) -> Person:
        try:
            response = self.people_table.get_item(Key={"name": name})
        except ClientError:
            logger.error("ClientError for Person with name=%r", name)  # noqa: TRY400
            raise
        if "Item" not in response:
            logger.warning("Person not found with name=%r", name)
            raise NotFoundError
        try:
            person = Person.model_validate(response.get("Item"))
        except ValidationError:
            logger.error("Invalid record for Person with name=%r, %s", name, response)  # noqa: TRY400
            raise
        return person
