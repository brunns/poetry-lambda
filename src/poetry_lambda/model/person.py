# type: ignore[reportIncompatibleVariableOverride]
import os

from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", "http://localhost:4566")


class Person(Model):
    class Meta:
        table_name = "People"
        host = DYNAMODB_ENDPOINT

    name = UnicodeAttribute(hash_key=True)
    nickname = UnicodeAttribute()
