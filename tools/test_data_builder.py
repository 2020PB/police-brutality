import pytest

from data_builder import title_to_name_date

tests = [
    {
        "description": 'title and date',
        "line": 'Title here | May 30th',
        "expected": ('Title here', '2020-05-30', 'May 30th')
    },
    {
        "description": 'title with no date',
        "line": 'Title here',
        "expected": ('Title here', '', '')
    },
    {
        "description": 'no title, only date',
        "line": ' | May 30th',
        "expected": ('', '2020-05-30', 'May 30th')
    },
    # edge case example
    {
        "description": 'no title, messed up date',
        "line": 'title | F 31',
        "expected": ('title', '', 'F 31')
    }
]


def test_title_to_name_date():
    for test in tests:
        result = title_to_name_date(test['line'])
        assert result == test['expected']
