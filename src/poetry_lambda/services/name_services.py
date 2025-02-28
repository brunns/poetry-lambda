from wireup import service

from poetry_lambda.repos.name_repo import NameRepo


@service
class NameService:
    def __init__(self, name_repo: NameRepo) -> None:
        super().__init__()
        self.name_repo = name_repo

    def get_nickname(self, name: str | None = None) -> str:
        if name:
            return self.name_repo.get_nickname(name)
        return "World"
