from contextlib import contextmanager
from pathlib import Path

import pytest


FILENAMES = tuple((Path(__file__).parent / "xml/getRecordings").iterdir())


@pytest.mark.parametrize(
    "filename", FILENAMES,
)
def test_video_count_always_present(mock_response, filename):
    from bbb_pymonitor.api import get_recordings

    with mock_response(filename):
        recordings = get_recordings()
        assert isinstance(recordings, list)
        for recording in recordings:
            assert "name" in recording
            assert "meetingID" in recording


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
