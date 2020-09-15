import pytest

from text_formatter import fix_common_misspellings


@pytest.mark.parametrize(
    "given_text, given_misspellings_dict, expected",
    [
        ("", {}, ""),
        ("something a word please", {}, "something a word please"),
        ("something a word please", {"word": "weeerd"}, "something a weeerd please"),
        (
            "something a word please. Nothing going on.",
            {"word": "weeerd", "noth": "nath"},
            "something a weeerd please. Nathing going on.",
        ),
    ],
)
def test_fix_common_misspellings(given_text, given_misspellings_dict, expected):
    assert expected == fix_common_misspellings(given_text, given_misspellings_dict)
