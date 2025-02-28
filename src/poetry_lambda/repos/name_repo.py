from wireup import service

from poetry_lambda.model.name import Name


@service
class NameRepo:
    def get_nickname(self, name: str) -> str:
        return Name.query(name).next().nickname
