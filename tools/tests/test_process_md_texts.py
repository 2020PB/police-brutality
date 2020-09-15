import pytest

from data_builder import process_md_texts


def test_handle_dc():
    data = {"Washington DC": "### Title | June 1st\n\nDescription of things \n\n**Links**\n\n* https://twitter.com/"}
    result = process_md_texts(data)

    assert result[0]["city"] == "DC"


def test_handle_missing_location():
    data = {"Unknown Location": "### Title | June 1st\n\nDescription of things \n\n**Links**\n\n* https://twitter.com/"}
    result = process_md_texts(data)

    assert result[0]["city"] == ""


def test_handle_missing_links(capsys):
    data = {
        "Washington DC": "### Title | June 1st\n\nDescription of things \n\n**Links**\n\n\n\n### Another Title | May 31\n\nDescription.\n\n**Links**\n\n"
    }
    with pytest.raises(ValueError):
        process_md_texts(data)
