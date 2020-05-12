"""Lifted from pypi's bigbluebutton-api-python
which was similar to
https://github.com/yunkaiwang/bigbluebutton-api-python/blob/master/bigbluebutton_api_python/util/urlbuilder.py
"""
from hashlib import sha1
from urllib.parse import quote_plus

import os
import requests
import xmltodict


BBB_SECRET = os.environ.get("BBB_SECRET")
BBB_URL = os.environ.get("BBB_URL")

if BBB_SECRET is None or BBB_URL is None:
    raise ValueError("Please provide a URL and a secret to connect to BBB")


class UrlBuilder:
    def __init__(self, bbbServerBaseUrl, securitySalt):
        self.securitySalt = securitySalt
        self.bbbServerBaseUrl = bbbServerBaseUrl

    def build_url(self, api_call, params={}):
        url = self.bbbServerBaseUrl
        url += api_call + "?"
        for key, value in params.items():
            if isinstance(value, bool):
                value = "true" if value else "false"
            else:
                value = str(value)
            url += key + "=" + quote_plus(value) + "&"

        url += "checksum=" + self.__get_checksum(api_call, params)
        return url

    def __get_checksum(self, api_call, params={}):
        secret_str = api_call
        for key, value in params.items():
            if isinstance(value, bool):
                value = "true" if value else "false"
            else:
                value = str(value)
            secret_str += key + "=" + quote_plus(value) + "&"
        if secret_str.endswith("&"):
            secret_str = secret_str[:-1]
        secret_str += self.securitySalt
        return sha1(secret_str.encode("utf-8")).hexdigest()


def get_meetings():
    """Invoke the API endpoint getMeetings, and convert the result
    to a list of dictionaries
    """
    builder = UrlBuilder(BBB_URL, BBB_SECRET)
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
