import urllib.parse

import requests
from lxml import html

from background_browser import BackgroundBrowser
from const import NON_BOT_USER_AGENT
from ninegag_basic_browser import NinegagBasicBrowser
from utils import random_wait

# Artificial delay to try to avoid being recognized as bots. Preferable use is before each GET request in the browser
ARTIFICIAL_AVERAGE_DELAY = 1.5  # Seconds.


# Does not work, use SeleniumNinegagBrowser
class NinegagBrowser(BackgroundBrowser, NinegagBasicBrowser):
    def get(self, url):
        random_wait(ARTIFICIAL_AVERAGE_DELAY)
        return self._non_delayed_get(url)

    def _non_delayed_get(self, url):
        # If url starts with '/' we stay at current host and adjust the request accordingly
        if self._host and url.startswith('/'):
            url = self._host + url

        # Performs the request
        response = requests.get(url, headers={'user-agent': NON_BOT_USER_AGENT})
        response.raise_for_status()  # If status code not ok, raises requests.exceptions.HTTPError

        # Updates attributes
        parsed_url = urllib.parse.urlparse(url)
        self._host = f'{parsed_url.scheme}://{parsed_url.netloc}'
        self._raw_html = response.text
        self._html = html.fromstring(self._raw_html)

    def scan_post(self):
        """
        Extracts useful data from a post, that its page was recently retrieved using get method

        Returns:
            NinegagPost: Representation of the current post
        """
        return self.scan_post_from_html(self._html, self._host)
