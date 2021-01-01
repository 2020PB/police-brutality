import pytest
from typing import Tuple

from data_builder import find_md_link_or_url, title_to_name_date, validate_geo


@pytest.mark.parametrize(
    "given, expected",
    [
        ("Title here | May 30th", ("Title here", "2020-05-30", "2020-05-30")),
        ("Title here | May 30th 2021", ("Title here", "2021-05-30", "2021-05-30")),
        ("Title here | Jan 15th", ("Title here", "2020-01-15", "2020-01-15")),
        ("Title here | (Believed to be) Jan 15th", ("Title here", "2020-01-15", "(Believed to be) 2020-01-15")),
        ("Title here | (Believed to be) 2020-01-15", ("Title here", "2020-01-15", "(Believed to be) 2020-01-15")),
        ("Title here | (believed to be) 2020-01-15", ("Title here", "2020-01-15", "(Believed to be) 2020-01-15")),
        ("Title here | 2020-01-15", ("Title here", "2020-01-15", "2020-01-15")),
        ("Title here | Date Unknown", ("Title here", "", "Unknown Date")),
        ("Title here | Unknown Date", ("Title here", "", "Unknown Date")),
    ],
)
def test_title_to_name_date__success_cases(given: str, expected: str) -> None:
    assert title_to_name_date(given) == expected


@pytest.mark.parametrize(
    "given",
    [
        (""),
        ("|"),
        ("| May 30th"),
        ("something something |"),
        ("Thing happened | this day | May 30th"),
        ("Title | Leb 21"),
        ("Title here | Unknown Datessssss"),
    ],
)
def test_title_to_name_date__error_cases(given: str) -> None:
    with pytest.raises(Exception):
        title_to_name_date(given)


@pytest.mark.parametrize(
    "given, expected",
    [
        ("", ("", "")),
        ("www.google.com", ("", "www.google.com")),
        ("ab[cd](ef)xy", ("abcdxy", "ef")),
        ("ab[cd](efxy", ("abcd", "efxy")),
        ("[abcd](efxy)", ("abcd", "efxy")),
        ("[abcd]zz(efxy)", ("abcdzz", "efxy")),
    ],
)
def test_find_md_link_or_url(given: str, expected: Tuple[str, str]) -> None:
    assert find_md_link_or_url(given) == expected


@pytest.mark.parametrize(
    "given",
    [
        ("a"),
        ("123"),
        ("-90., -180."),
        ("+90.1, -100.111"),
        ("-91, 123.456"),
        ("045, 180"),
        ("45, 180"),
        ("+90.0, -127.5543"),
        ("+90.0, -127.55433456"),
    ],
)
def test_validate_geo_fail(given: str) -> None:
    with pytest.raises(Exception):
        validate_geo(given)


@pytest.mark.parametrize(
    "given, expected",
    [
        ("", ""),
        (" ", ""),
        ("+90.0, -127.554334", "90.0, -127.554334"),
        ("+90.0, -127.55433", "90.0, -127.55433"),
        ("+90.0, -127.5543345", "90.0, -127.5543345"),
        ("45.1234567, 180", "45.1234567, 180"),
        ("-90, -180", "-90, -180"),
        ("-90.000, -180.0000", "-90.000, -180.0000"),
        ("90, 180", "90, 180"),
        ("47.1231231, 179.9999999", "47.1231231, 179.9999999"),
    ],
)
def test_validate_geo_success(given: str, expected: str) -> None:
    assert expected == validate_geo(given)
