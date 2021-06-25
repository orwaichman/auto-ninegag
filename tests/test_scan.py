import pytest

from tests import TestingNinegagBrowser


@pytest.mark.dependency()
def test_first_post():
    with TestingNinegagBrowser() as ninegag_browser:
        # Assumes test_basic_actions.test_go_to_section() is successful
        ninegag_browser.go_to_section('funny')
        ninegag_browser.driver.get(ninegag_browser._find_first_post())


@pytest.mark.dependency(depends=['test_first_post'])
def test_scan_post():
    with TestingNinegagBrowser() as ninegag_browser:
        ninegag_browser._scan_post()


@pytest.mark.dependency(depends=['test_first_post'])
def test_next_post():
    with TestingNinegagBrowser() as ninegag_browser:
        ninegag_browser._next_post()
