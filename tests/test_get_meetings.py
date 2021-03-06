from contextlib import contextmanager
from pathlib import Path

import pytest


FILENAMES = tuple((Path(__file__).parent / "xml/getMeetings").iterdir())


@pytest.mark.parametrize(
    "filename", FILENAMES,
)
def test_video_count_always_present(mock_response, filename):
    from bbb_pymonitor.api import get_meetings

    with mock_response(filename):
        meetings = get_meetings()
        assert isinstance(meetings, list)
        for meeting in meetings:
            assert "videoCount" in meeting


@pytest.fixture
def mock_response(mocker, monkeypatch):
    @contextmanager
    def do_mock(filename):
        """Mock requests.get so that the returned response has the text
        taken from `filename` in this directory.
        """
        import requests

        mocker.patch("requests.get")
        requests.get().text = (Path(__file__).parent / filename).read_text()
        yield

    monkeypatch.setenv("BBB_URL", "foo")
    monkeypatch.setenv("BBB_SECRET", "bar")
    return do_mock
