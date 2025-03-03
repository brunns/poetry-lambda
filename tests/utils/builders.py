import factory

from poetry_lambda.model.person import Person


class PersonFactory(factory.Factory):
    class Meta:
        model = Person

    name = "simon"
    nickname = "Baldy"
