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
    (
        ' | May 30th',
        ('', '2020-05-30', 'May 30th')
    )
]


@pytest.mark.parametrize("input,expected", tests)
def test_title_to_name_date(input, expected):
    assert title_to_name_date(input) == expected


# failing test
def test_handle_weird_dateFormat():
    with pytest.raises(AttributeError):
        title_to_name_date('title | 00')
