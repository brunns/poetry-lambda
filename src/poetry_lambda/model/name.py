# type: ignore[reportIncompatibleVariableOverride]
import os

from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

DYNAMODB_ENDPOINT = os.getenv("DYNAMODB", "http://localhost:4566")


class Name(Model):
    class Meta:
        table_name = "Names"
        region = "eu-west-1"
        host = DYNAMODB_ENDPOINT

    name = UnicodeAttribute(hash_key=True)
    nickname = UnicodeAttribute()
