from .api import get_meetings
from rich.console import Console
from rich.table import Table
from rich.text import Text

import logging
import os
import requests
import sys


logger = logging.getLogger()


def get_empty_meeting_table():
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Title", style="dim")
    table.add_column("Moderators", justify="right")
    table.add_column("Participants", justify="right")
    table.add_column("Video", justify="right")
    table.add_column("Voice", justify="right")
    table.add_column("Recording", justify="right")
    table.add_column("Created")
    return table


def get_summary_table(meetings):
    table = get_empty_meeting_table()
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

    for attendee in meeting["attendees"]["attendee"]:
        table.add_row(
            attendee["fullName"],
            attendee["role"],
            render_bool(attendee["isPresenter"]),
            render_bool(attendee["isListeningOnly"]),
            render_bool(attendee["hasJoinedVoice"]),
            render_bool(attendee["hasVideo"]),
        )
    return table


def send_influxdb(meetings):
    influx_url = os.environ.get("INFLUXDB_URL")
    influx_pass = os.environ.get("INFLUXDB_PASS")
    influx_user = os.environ.get("INFLUXDB_USER")
    response = requests.get(
        influx_url + "/query",
        params={"q": "SHOW DATABASES"},
        auth=(influx_user, influx_pass),
    )
    total_video = sum(map(lambda x: int(x["videoCount"]), meetings))
    total_participants = sum(map(lambda x: int(x["participantCount"]), meetings))
    total_voice = sum(map(lambda x: int(x["voiceParticipantCount"]), meetings))
    payload = f"room_info,host=moscote video={total_video},participants={total_participants},voice={total_voice}"
    logger.debug(f"Sending measurement {payload}")
    response = requests.post(
        influx_url + "/api/v2/write?bucket=bbb",
        auth=(influx_user, influx_pass),
        data=payload,
    )
    if response.status_code < 300:
        logger.error(response.text)


def main():
    console = Console()
    meetings = get_meetings()
    for meeting in meetings:
        console.print(get_meeting_info(meeting))
    console.print(get_summary_table(meetings))
    if "--send" in sys.argv:
        console.print("Sending metrics to influxdb")
        send_influxdb(meetings)
