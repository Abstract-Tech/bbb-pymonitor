from bigbluebutton_api_python import BigBlueButton

import os


BBB_SECRET = os.environ.get("BBB_SECRET")
BBB_URL = os.environ.get("BBB_URL")

if BBB_SECRET is None or BBB_URL is None:
    raise ValueError("Please provide a URL and a secret to connect to BBB")

client = BigBlueButton(BBB_URL, BBB_SECRET)


def get_meetings():
    response = client.get_meetings()
    meetings = []

    if "meeting" in response["xml"]["meetings"]:
        response_meetings = response["xml"]["meetings"]["meeting"]
    else:
        response_meetings = []
    for meeting in response_meetings:
        meeting_dict = {"name": meeting["meetingName"].get_cdata()}
        keys = [
            "participantCount",
            "listenerCount",
            "voiceParticipantCount",
            "videoCount",
            "maxUsers",
            "moderatorCount",
        ]
        for key in keys:
            meeting_dict[key] = int(meeting[key].get_cdata())
        meetings.append(meeting_dict)

    return meetings


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_meetings())
