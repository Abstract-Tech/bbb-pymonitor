"""Lifted from pypi's bigbluebutton-api-python
which was similar to
https://github.com/yunkaiwang/bigbluebutton-api-python/blob/master/bigbluebutton_api_python/util/urlbuilder.py
"""
from hashlib import sha1
from urllib.parse import quote_plus


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
