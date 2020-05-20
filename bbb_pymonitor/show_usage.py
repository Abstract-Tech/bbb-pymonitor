from .api import BBB_HOST
from .api import get_meetings
from .api import get_recordings
from .api import RECORDING_STATES
from collections import Counter
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.text import Text

import arrow
import logging
import math
import os
import requests
import sys


logger = logging.getLogger()


def get_summary_table(meetings):
    table = Table(show_header=True, header_style="bold green", title="Summary")
    table.add_column("Title", style="dim")
    table.add_column("Moderators", justify="right")
    table.add_column("Participants", justify="right")
    table.add_column("Video", justify="right")
    table.add_column("Voice", justify="right")
    table.add_column("Recording", justify="right")
    table.add_column("Created")
    totals = (0,) * 4
    total_recording = 0
    for meeting in meetings:
        recording = "N"
        if "recording" in meeting and meeting["recording"]:
            recording = "Y"
            total_recording += 1
        table.add_row(
            meeting.get("meetingName", "-"),
            str(meeting["moderatorCount"]),
            str(meeting["participantCount"]),
            str(meeting["videoCount"]),
            str(meeting["voiceParticipantCount"]),
            recording,
            str(meeting["createDate"]),
        )

        totals = tuple(
            map(
                sum,
                zip(
                    totals,
                    [
                        int(meeting["moderatorCount"]),
                        int(meeting["participantCount"]),
                        int(meeting["videoCount"]),
                        int(meeting["voiceParticipantCount"]),
                    ],
                ),
            )
        )
    table.add_row("Total", *map(str, totals + (total_recording,)))
    return table


def render_bool(value):
    if value == "true":
        return Text("✓", style="bold green")
    else:
        return Text("✗", style="red")


def get_meeting_info(meeting):
    if not meeting["attendees"]:
        return Text('{meeting["meetingName"]} (no attendees)')
    table = Table(
        show_header=True, header_style="bold green", title=meeting["meetingName"]
    )
    table.add_column("Name", style="dim")
    table.add_column("Role", justify="right")
    table.add_column("Presenter", justify="right")
    table.add_column("Listen only", justify="right")
    table.add_column("Voice", justify="right")
    table.add_column("Video", justify="right")
    attendees = meeting["attendees"]["attendee"]
    if not isinstance(attendees, list):
        attendees = [attendees]
    for attendee in attendees:
        table.add_row(
            attendee["fullName"],
            attendee["role"],
            render_bool(attendee["isPresenter"]),
            render_bool(attendee["isListeningOnly"]),
            render_bool(attendee["hasJoinedVoice"]),
            render_bool(attendee["hasVideo"]),
        )
    return table


def send_influxdb(meetings=(), recordings=()):
    influx_url = os.environ.get("INFLUXDB_URL")
    influx_pass = os.environ.get("INFLUXDB_PASS")
    influx_user = os.environ.get("INFLUXDB_USER")
    total_video = sum(map(lambda x: int(x["videoCount"]), meetings))
    total_participants = sum(map(lambda x: int(x["participantCount"]), meetings))
    total_voice = sum(map(lambda x: int(x["voiceParticipantCount"]), meetings))
    payload = f"room_info,host={BBB_HOST} video={total_video},participants={total_participants},voice={total_voice}"
    recordings_count = Counter({a: 0 for a in RECORDING_STATES})
    recordings_count.update(map(lambda x: x["state"], recordings))
    recording_stats = ",".join(f"{key}={val}" for key, val in recordings_count.items())
    payload += f"\nrecording_info,host={BBB_HOST} {recording_stats}"
    logger.debug(f"Sending measurement {payload}")
    response = requests.post(
        influx_url + "/api/v2/write?bucket=bbb",
        auth=(influx_user, influx_pass),
        data=payload,
    )
    if response.status_code >= 300:
        logger.error(response.text)


def get_recordings_info(recordings_unsorted):
    recordings = sorted(recordings_unsorted, key=lambda x: x["startTime"])
    table = Table(show_header=True, header_style="bold green", title="Recordings")
    table.add_column("Name")
    table.add_column("State")
    table.add_column("Size")
    table.add_column("Raw Size")
    table.add_column("Started")
    table.add_column("Duration")
    table.add_column("Origin")

    for recording in recordings:
        duration = get_duration(recording)
        metadata = recording.get("metadata", {}) or {}
        table.add_row(
            metadata.get("name", recording["name"]),
            fmt_state(recording["state"]),
            fmt_size(recording["size"]),
            fmt_size(recording["rawSize"]),
            fmt_dt(recording["startTime"]),
            duration,
            metadata.get("bbb-origin", ""),
        )
    return table


def fmt_state(state):
    return {
        "published": Text(state, style="green"),
        "deleted": Text(state, style="red"),
    }.get(state, state)


def from_epoch(dt_as_str):
    """Convert a string representing time in milliseconds from EPOCH
    to an arrow object
    """
    return arrow.get(int(dt_as_str) / 1000)


def get_duration(recording):
    return from_epoch(recording["endTime"]).humanize(
        from_epoch(recording["startTime"]), only_distance=True
    )


def fmt_dt(num_as_str, suffix="B"):
    """Format an integer number (can be passed as a string)
    as a datetime in milliseconds from EPOCH.
    """
    return arrow.get(int(num_as_str) / 1000).humanize()


def fmt_size(num_as_str, suffix="B"):
    """Format an integer number using KiB/MiB etc suffix
    """
    num = int(num_as_str)
    magnitude = 0
    if num != 0:
        magnitude = int(math.floor(math.log(num, 1024)))
    val = num / math.pow(1024, magnitude)
    if magnitude > 7:
        return "{:.1f}{}{}".format(val, "Yi", suffix)
    return "{:3.1f} {}{}".format(
        val, ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"][magnitude], suffix
    )


def main():
    setup_logging()
    console = Console()

    recordings = get_recordings()
    console.print(get_recordings_info(recordings))

    meetings = get_meetings()
    for meeting in meetings:
        console.print(get_meeting_info(meeting))

    console.print(get_summary_table(meetings))

    if "--send" in sys.argv:
        console.print("Sending metrics to influxdb")
        send_influxdb(meetings=meetings, recordings=recordings)


def setup_logging():
    FORMAT = "%(message)s"
    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "WARN"),
        format=FORMAT,
        datefmt="[%X] ",
        handlers=[RichHandler()],
    )
