from wireup import service

from poetry_lambda.model.person import Person


@service
class PersonRepo:
    def get_nickname(self, name: str) -> str:
        return Person.query(name).next().nickname
