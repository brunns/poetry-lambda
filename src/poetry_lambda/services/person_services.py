from wireup import service

from poetry_lambda.repos.person_repo import PersonRepo


@service
class PersonService:
    def __init__(self, person_repo: PersonRepo) -> None:
        super().__init__()
        self.person_repo = person_repo

    def get_nickname(self, name: str | None = None) -> str:
        if name:
            return self.person_repo.get_nickname(name)
        return "World"
