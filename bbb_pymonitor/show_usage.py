from .urlbuilder import UrlBuilder
from rich.console import Console
from rich.table import Table

import os
import requests
import xmltodict


BBB_SECRET = os.environ.get("BBB_SECRET")
BBB_URL = os.environ.get("BBB_URL")

if BBB_SECRET is None or BBB_URL is None:
    raise ValueError("Please provide a URL and a secret to connect to BBB")

builder = UrlBuilder(BBB_URL, BBB_SECRET)


def get_meetings():
    response = xmltodict.parse(requests.get(builder.build_url("getMeetings")).text)

    meetings = []
    response_meetings = response["response"]["meetings"]
    if response_meetings is None:
        return meetings
    for meeting in response_meetings.values():
        int_keys = [
            "listenerCount",
            "maxUsers",
            "moderatorCount",
            "participantCount",
            "videoCount",
            "voiceParticipantCount",
        ]
        for key in meeting:
            if key in int_keys:
                meeting[key] = int(meeting[key])
        meetings.append(meeting)

    return meetings


def get_meetings_table(meetings):
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Title", style="dim")
    table.add_column("Moderators", justify="right")
    table.add_column("Participants", justify="right")
    table.add_column("Video", justify="right")
    table.add_column("Voice", justify="right")
    table.add_column("Created")
    totals = [0] * 4
    for meeting in meetings:
        table.add_row(
            meeting["meetingName"],
            str(meeting["moderatorCount"]),
            str(meeting["participantCount"]),
            str(meeting["videoCount"]),
            str(meeting["voiceParticipantCount"]),
            str(meeting["createDate"]),
        )
        totals = tuple(
            map(
                sum,
                zip(
                    totals,
                    [
                        meeting["moderatorCount"],
                        meeting["participantCount"],
                        meeting["videoCount"],
                        meeting["voiceParticipantCount"],
                    ],
                ),
            )
        )
    table.add_row("Total", *map(str, totals))
    return table


def main():
    console = Console()
    console.print(get_meetings_table(get_meetings()))
