from poetry_lambda.services import NameService


def test_something():
    # Given
    ns = NameService()

    # When
    actual = ns.get_name()

    # Then
    assert actual == "World"
