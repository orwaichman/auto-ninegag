from const import WEBDRIVER_PATH
from ninegag_selenium_browser import NinegagSeleniumBrowser


# Modifying NinegagBrowser used for testing to be a single instance class that can only be closed explicitly
class TestingNinegagBrowser(NinegagSeleniumBrowser):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._start(executable_path=WEBDRIVER_PATH)
        return cls._instance

    def __init__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
