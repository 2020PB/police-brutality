import pytest

from data_builder import title_to_name_date

tests = [
    (
        'Title here | May 30th',
        ('Title here', '2020-05-30', 'May 30th')
    ),
    (
        'Title here',
        ('Title here', '', '')
    ),
]


@pytest.mark.parametrize("input,expected", tests)
def test_title_to_name_date(input, expected):
    assert title_to_name_date(input) == expected


def test_handle_missing_name(capsys):
    title_missing_name = '| May 30th'
    title_to_name_date(title_missing_name)

    captured = capsys.readouterr()
    assert "Failed name parse: missing name for" in str(captured) 


@pytest.mark.skip(reason="failing test, need to handle this case")
def test_handle_name_with_multiple_pipes():
    malformed_title = 'Thing happened | this day | May 30th'
    result = title_to_name_date(malformed_title)
    # what should happen here?


def test_handle_missing_date(capsys):
    title_missing_date = 'Title thinger'
    title_to_name_date(title_missing_date)

    captured = capsys.readouterr()
    assert "Failed date parse: missing date for" in str(captured)


def test_handle_weird_date_format(capsys):
    title_with_bad_date = 'Title | Leb 21'

    result = title_to_name_date(title_with_bad_date)
    captured = capsys.readouterr()
    assert "Failed date format parse for title" in str(captured)


@pytest.mark.skip(reason="failing test, need to handle this case")
def test_handle_nonexistant_date():
    title_with_bad_date = 'Title | February 31st'

    result = title_to_name_date(title_with_bad_date)
    # what should happen here?
