from bbb_pymonitor.api import parse_getmeeting_response
from bbb_pymonitor.api import parse_recordings
from pathlib import Path
from rich.console import Console

import pytest


GETMEETINGS_EXAMPLES = [
    (el.name, parse_getmeeting_response(el.read_text()))
    for el in ((Path(__file__).parent / "xml/getMeetings").iterdir())
]
GETRECORDINGS_EXAMPLES = [
    (el.name, parse_recordings(el.read_text()))
    for el in ((Path(__file__).parent / "xml/getRecordings").iterdir())
]


@pytest.mark.parametrize(
    "name,example", GETMEETINGS_EXAMPLES,
)
def test_meetings_smoketest(name, example):
    from bbb_pymonitor.show_usage import get_summary_table
    from bbb_pymonitor.show_usage import get_meeting_info

    get_summary_table(example)
    for meeting in example:
        get_meeting_info(meeting)


@pytest.mark.parametrize(
    "name,example", GETRECORDINGS_EXAMPLES,
)
def test_recordings_smoketest(name, example):
    from bbb_pymonitor.show_usage import get_recordings_info

    table = get_recordings_info(example)
    console = Console(record=True, width=120)
    console.print()
    console.print(table)


def test_get_summary():
    from bbb_pymonitor.show_usage import get_summary_table

    meetings = dict(GETMEETINGS_EXAMPLES)["two-meetings.xml"]

    table = get_summary_table(meetings)
    console = Console(record=True, width=120)
    console.print()
    console.print(table)
    text = console.export_text()
    assert "John's room" in text
    assert "A room" in text


def test_get_meeting():
    from bbb_pymonitor.show_usage import get_meeting_info

    meetings = dict(GETMEETINGS_EXAMPLES)["manypeople.xml"]

    table = get_meeting_info(meetings[0])
    console = Console(record=True, width=120)
    console.print()
    console.print(table)
    text = console.export_text()
    assert "Professor Chaos" in text
    assert "World Domination discussion" in text


def test_get_recordings():
    from bbb_pymonitor.show_usage import get_recordings_info

    recordings = dict(GETRECORDINGS_EXAMPLES)["one.xml"]
    table = get_recordings_info(recordings)
    console = Console(record=True, width=120)
    console.print()
    console.print(table)
    text = console.export_text()
    assert "ACME stakeholders meeting" in text
    assert "Greenlight" in text
    assert "breakfast" in text
