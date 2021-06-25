import pytest

from tests import TestingNinegagBrowser


def test_activate_nightmode():
    with TestingNinegagBrowser() as ninegag_browser:
        ninegag_browser.activate_nightmode()


@pytest.mark.parametrize('section', ['Funny', 'hot'])
def test_go_to_section(section):
    with TestingNinegagBrowser() as ninegag_browser:
        ninegag_browser.go_to_section(section)
