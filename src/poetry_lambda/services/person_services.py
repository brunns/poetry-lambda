from wireup import service

from poetry_lambda.repos.exceptions import NotFoundError
from poetry_lambda.repos.person_repo import PersonRepo


class UnknownPersonError(Exception):
    pass


@service
class PersonService:
    def __init__(self, person_repo: PersonRepo) -> None:
        super().__init__()
        self.person_repo = person_repo

    def get_nickname(self, name: str | None = None) -> str:
        if name:
            try:
                person = self.person_repo.get_person(name)
            except NotFoundError as e:
                raise UnknownPersonError from e
            else:
                return person.nickname
        return "World"
