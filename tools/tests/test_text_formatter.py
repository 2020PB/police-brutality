import pytest
from typing import List, Dict, Set

from text_formatter import fix_common_misspellings, format_tags, WNL


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
def test_fix_common_misspellings(given_text: str, given_misspellings_dict: Dict[str, str], expected: str) -> None:
    assert expected == fix_common_misspellings(given_text, given_misspellings_dict)


@pytest.mark.parametrize(
    "given_text, given_all_tags, given_tag_overrides, expected",
    [
        ([""], set(), {}, ""),
        (["    "], set(), {}, ""),
        (["protester"], {"protester"}, {}, "protester"),
        (["protesters"], {"protester"}, {}, "protester"),
        (["protesters"], {"protester"}, {}, "protester"),
        (["protesters"], {"protester"}, {"protesters": "soup"}, "protester"),
        (
            ["protesters", "banana", "tear-gas", "rubbers-bullets"],
            {"protester", "banana", "tear-gas", "rubber-bullet"},
            {},
            "banana, less-lethal, protester, rubber-bullet, tear-gas",
        ),
        (
            ["protesters", "banana", "tear-gas", "rubbers-bullets", "less-lethal"],
            {"protester", "banana", "tear-gas", "rubber-bullet", "less-lethal"},
            {"le-lethal": "less-lethal"},
            "banana, less-lethal, protester, rubber-bullet, tear-gas",
        ),
    ],
)
def test_format_tags(
    given_text: List[str], given_all_tags: Set[str], given_tag_overrides: Dict[str, str], expected: str
) -> None:
    assert expected == format_tags(WNL, given_all_tags, given_tag_overrides, given_text)


@pytest.mark.parametrize(
    "given_tags, given_all_tags, given_tag_overrides",
    [(["protestesdfsdfr"], set("protester"), {}), (["protesters"], {"protester"}, {"protester": "soup"})],
)
def test_format_tags__error(
    given_tags: List[str], given_all_tags: Set[str], given_tag_overrides: Dict[str, str]
) -> None:
    with pytest.raises(ValueError):
        format_tags(WNL, given_all_tags, given_tag_overrides, given_tags)
