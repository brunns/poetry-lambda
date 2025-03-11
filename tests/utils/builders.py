import factory

from poetry_lambda.model.person import Person


class PersonFactory(factory.Factory):
    class Meta:
        model = Person

    name = factory.Faker("first_name")
    nickname = factory.Faker("first_name")
