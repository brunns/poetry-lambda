from unittest.mock import MagicMock

from poetry_lambda.repos.name_repo import NameRepo
from poetry_lambda.services import NameService


def test_name_service_returns_default():
    # Given
    name_repo = MagicMock(spec=NameRepo)
    ns = NameService(name_repo)

    # When
    actual = ns.get_nickname(None)

    # Then
    assert actual == "World"


def test_name_service_returns_from_repo():
    # Given
    name_repo = MagicMock(spec=NameRepo)
    name_repo.get_nickname = MagicMock(return_value="Baldy Head")
    ns = NameService(name_repo)

    # When
    actual = ns.get_nickname("simon")

    # Then
    assert actual == "Baldy Head"
