from .urlbuilder import UrlBuilder
from rich.console import Console
from rich.table import Table
from rich.text import Text

import os
import requests
import xmltodict


BBB_SECRET = os.environ.get("BBB_SECRET")
BBB_URL = os.environ.get("BBB_URL")

if BBB_SECRET is None or BBB_URL is None:
    raise ValueError("Please provide a URL and a secret to connect to BBB")

builder = UrlBuilder(BBB_URL, BBB_SECRET)


def get_meetings():
    url = builder.build_url("getMeetings")
    text = requests.get(url).text
    response = xmltodict.parse(text)

    response_meetings = response["response"]["meetings"]
    if response_meetings is None:
        return []
    response_meetings.values()
    if "meeting" in response_meetings:
        if "meetingName" in response_meetings["meeting"]:
            return [response_meetings["meeting"]]
        return response_meetings["meeting"]


def get_meetings_table(meetings):
    table = Table(show_header=True, header_style="bold green")
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


def main():
    console = Console()
    console.print(get_meetings_table(get_meetings()))
