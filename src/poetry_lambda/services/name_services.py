from wireup import service


@service
class NameService:
    def get_name(self) -> str:
        return "World"
