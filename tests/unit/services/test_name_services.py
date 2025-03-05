from unittest.mock import MagicMock

import pytest

from poetry_lambda.model.person import Person
from poetry_lambda.repos.exceptions import NotFoundError
from poetry_lambda.repos.person_repo import PersonRepo
from poetry_lambda.services import PersonService
from poetry_lambda.services.person_services import UnknownPersonError


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
    person_repo.get_person = MagicMock(return_value=Person(name="simon", nickname="Baldy Head"))
    ps = PersonService(person_repo)

    # When
    actual = ps.get_nickname("simon")

    # Then
    assert actual == "Baldy Head"


def test_person_service_for_nonexistent_name():
    # Given
    person_repo = MagicMock(spec=PersonRepo)
    person_repo.get_person = MagicMock(side_effect=NotFoundError)
    ps = PersonService(person_repo)

    # When
    with pytest.raises(UnknownPersonError):
        ps.get_nickname("fred")
