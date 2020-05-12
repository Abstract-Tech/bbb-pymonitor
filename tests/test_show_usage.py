from bbb_pymonitor.api import parse_getmeeting_response
from pathlib import Path
from rich.console import Console

import pytest


EXAMPLES = [
    (el.name, parse_getmeeting_response(el.read_text()))
    for el in ((Path(__file__).parent / "xml/getMeetings").iterdir())
]


@pytest.mark.parametrize(
    "name,example", EXAMPLES,
)
def test_smoketest(name, example):
    from bbb_pymonitor.show_usage import get_summary_table
    from bbb_pymonitor.show_usage import get_meeting_info

    get_summary_table(example)
    for meeting in example:
        get_meeting_info(meeting)


def test_get_summary():
    from bbb_pymonitor.show_usage import get_summary_table

    meetings = dict(EXAMPLES)["two-meetings.xml"]

    table = get_summary_table(meetings)
    console = Console(record=True, width=120)
    console.print()
    console.print(table)
    text = console.export_text()
    assert "John's room" in text
    assert "A room" in text


def test_get_meeting():
    from bbb_pymonitor.show_usage import get_meeting_info

    meetings = dict(EXAMPLES)["manypeople.xml"]

    table = get_meeting_info(meetings[0])
    console = Console(record=True, width=120)
    console.print()
    console.print(table)
    text = console.export_text()
    assert "Professor Chaos" in text
    assert "World Domination discussion" in text
