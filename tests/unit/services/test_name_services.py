from unittest.mock import MagicMock

from poetry_lambda.repos.person_repo import PersonRepo
from poetry_lambda.services import PersonService


def test_person_service_returns_default():
    # Given
    person_repo = MagicMock(spec=PersonRepo)
    ps = PersonService(person_repo)

    # When
    actual = ps.get_nickname(None)

    # Then
    assert actual == "World"


def test_person_service_returns_from_repo():
    # Given
    person_repo = MagicMock(spec=PersonRepo)
    person_repo.get_nickname = MagicMock(return_value="Baldy Head")
    ps = PersonService(person_repo)

    # When
    actual = ps.get_nickname("simon")

    # Then
    assert actual == "Baldy Head"
