import pytest

from journi.main import JourniListProxyModel


@pytest.fixture
def jlpm():
    return JourniListProxyModel()

def test_entry_time_format(jlpm):
    formatted_time = jlpm.format_entry_time(1500000000)
    assert(formatted_time == "2017-07-14")

def test_entry_abstract_format(jlpm):
    text = "abcdefghijklmnopqrstuvwxyz"
    formatted_no_elipsis = jlpm.format_entry_abstract(text[:19])
    assert(formatted_no_elipsis == text[:19])
    formatted_with_elipsis = jlpm.format_entry_abstract(text)
    assert(formatted_with_elipsis == text[:20]+"…")
