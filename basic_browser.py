import contextlib

from exceptions import NoSuchElement


class BasicBrowser(contextlib.AbstractContextManager):
    def __init__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _get(self, url):
        return self._non_delayed_get(url)

    def _non_delayed_get(self, url):
        raise NotImplemented

    def _find_element_by_xpath(self, xpath):
        elements = self._find_elements_by_xpath(xpath)
        if not elements:
            raise NoSuchElement(f'Could not find element "{xpath}"')
        return elements[0]

    def _find_elements_by_xpath(self, xpath):
        raise NotImplemented

    @staticmethod
    def _get_element_attribute(element, attr):
        raise NotImplemented

    @staticmethod
    def _get_element_text(element):
        raise NotImplemented

    def _click_link(self, element):
        url = self._get_element_attribute(element, 'href')
        self._get(url)
