import pytest

from data_rewriter import validate_geo


@pytest.mark.parametrize(
    "given", [("a"), ("123"), ("-90., -180."), ("+90.1, -100.111"), ("-91, 123.456"), ("045, 180")]
)
def test_validate_geo_fail(given: str) -> None:
    with pytest.raises(Exception):
        validate_geo(given)


@pytest.mark.parametrize(
    "given, expected",
    [
        ("", ""),
        (" ", ""),
        ("+90.0, -127.554334", "(+90.0, -127.554334)"),
        ("45, 180", "(+45, +180)"),
        ("-90, -180", "(-90, -180)"),
        ("-90.000, -180.0000", "(-90.000, -180.0000)"),
        ("90, 180", "(+90, +180)"),
        ("47.1231231, 179.99999999", "(+47.1231231, +179.99999999)"),
    ],
)
def test_validate_geo_fail(given: str, expected: str) -> None:
    assert expected == validate_geo(given)
