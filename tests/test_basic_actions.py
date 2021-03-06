import pytest

from tests import TestingNinegagBrowser


def test_click_nightmode_button():
    with TestingNinegagBrowser() as ninegag_browser:
        ninegag_browser.click_nightmode_button()
        ninegag_browser.click_nightmode_button()


@pytest.mark.parametrize('section', ['Funny', 'hot'])
def test_go_to_section(section):
    with TestingNinegagBrowser() as ninegag_browser:
        ninegag_browser.go_to_section(section)
