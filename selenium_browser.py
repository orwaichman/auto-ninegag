from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from basic_browser import BasicBrowser
from exceptions import NoSuchElement

MAX_DELAY = 7  # Seconds


class SeleniumBrowser(BasicBrowser):

    def __init__(self, **options):
        super().__init__()
        self._start(**options)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._quit()

    def _start(self, **options):
        """
        Opens a new WebDriver instance
        """
        self._driver = webdriver.Firefox(**options)
        self._driver.maximize_window()

    def _quit(self):
        self._driver.quit()

    def _non_delayed_get(self, url):
        self._driver.get(url)

    def _find_element_by_xpath(self, xpath):
        try:
            return self._driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            raise NoSuchElement(f'Could not find element "{xpath}"')

    def _find_elements_by_xpath(self, xpath):
        return self._driver.find_elements_by_xpath(xpath)

    @staticmethod
    def _get_element_attribute(element, attr):
        return element.get_attribute(attr)

    @staticmethod
    def _get_element_text(element):
        return element.get_attribute('textContent')

    def _wait_for_elements(self, xpath):
        """
        Waits for elements to load and fetches them

        Args:
            xpath (str):

        Returns:
            list[WebElement]
        """
        try:
            WebDriverWait(self._driver, MAX_DELAY).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return self._find_elements_by_xpath(xpath)
        except TimeoutException:
            return []

    def _wait_for_element(self, xpath):
        elements = self._wait_for_elements(xpath)
        if not elements:
            raise NoSuchElement(f'Could not find element "{xpath}"')
        return elements[0]
