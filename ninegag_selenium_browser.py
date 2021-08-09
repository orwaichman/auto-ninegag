import itertools
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from ninegag_basic_browser import NinegagBasicBrowser
from selenium_browser import SeleniumBrowser
from const import NINEGAG_URL, NinegagXPaths
from exceptions import AuthenticationRequired, InvalidAction
from utils import random_wait

MAX_DELAY = 10  # Seconds
MAX_ATTEMPTS_FOR_ACTION = 5
# Artificial delay to try to avoid being recognized as bots. Preferable use is before each GET request in the browser
ARTIFICIAL_AVERAGE_DELAY = 0.5  # Seconds.


class NinegagSeleniumBrowser(SeleniumBrowser, NinegagBasicBrowser):
    def _get(self, url):
        random_wait(ARTIFICIAL_AVERAGE_DELAY)
        return self._non_delayed_get(url)

    def _start(self, **options):
        """
        Opens a new WebDriver instance and browses to 9GAG homepage
        """
        super()._start(**options)
        self._get(NINEGAG_URL)

    def go_to_section(self, section_name: str, fresh: bool = False):
        """
        Browse to a section URL
        Args:
            section_name (str): 9GAG section name as appears in the menu or in the URL, works with both
            fresh (bool): Whether to browse to section's Fresh (otherwise goes to Hot)
        """
        if section_name.lower() in ('hot', 'trending', 'fresh'):
            self._get(f'{NINEGAG_URL}/{section_name.lower()}')
            return

        try:
            self._find_element_by_xpath(NinegagXPaths.SECTION_LIST)
        except NoSuchElementException:
            raise NoSuchElementException('Could not find 9GAG menu, perhaps window is not wide enough')

        try:
            link = self._find_element_by_xpath(f'{NinegagXPaths.SECTION_LIST_ITEM}[contains(text(), "{section_name.capitalize()}")]')
            self._get(f'{self._get_element_attribute(link, "href")}{"/fresh" if fresh else ""}')
            return
        except NoSuchElementException:
            pass

        try:
            link = self._find_element_by_xpath(f'{NinegagXPaths.SECTION_LIST_ITEM}[@href="/{section_name.lower()}"]')
            self._get(f'{self._get_element_attribute(link, "href")}{"/fresh" if fresh else ""}')
            return
        except NoSuchElementException:
            raise InvalidAction(f'Section "{section_name}" was not found')

    def click_nightmode_button(self):
        """
        Turns night mode on or off
        """
        self._find_element_by_xpath(NinegagXPaths.NIGHT_MODE_BUTTON).click()

    def login(self, username: str, password: str):
        """
        Authenticate to 9GAG
        Args:
            username (str): Account's username or email
            password (str): Account's password
        """
        self._find_element_by_xpath(NinegagXPaths.LOGIN_LINK).click()
        self._login(username, password)

    def _login(self, username: str, password: str):
        """
        Authenticate to 9GAG
        Notes:
            * Assumes login frame is displayed in driver

        Args:
            username (str): Account's username or email
            password (str): Account's password
        """
        # Wait until frame is loaded
        username_input = WebDriverWait(self._driver, MAX_DELAY).until(
            EC.presence_of_element_located((By.XPATH, NinegagXPaths.LoginFrame.USERNAME_INPUT)))
        username_input.send_keys(username)

        self._find_element_by_xpath(NinegagXPaths.LoginFrame.PASSWORD_INPUT).send_keys(password)

        self._find_element_by_xpath(NinegagXPaths.LoginFrame.SUBMIT_BUTTON).click()

    def upvote(self):
        """
        Performs an upvote on a post
        Notes:
            * Assumes webdriver is in a post page
        """
        self._authenticated_action_click(NinegagXPaths.Post.UPVOTE_BUTTON, 'Upvoting')

    def downvote(self):
        """
        Performs a downvote on a post
        Notes:
            * Assumes webdriver is in a post page
        """
        self._authenticated_action_click(NinegagXPaths.Post.DOWNVOTE_BUTTON, 'Downvoting')

    def _authenticated_action_click(self, element_xpath: str, action_str: str, username=None, password=None):
        """
        Generic handling with clicking on an element that results in login popup if user is not authenticated
        Args:
            element_xpath (str):
            action_str (str): How is the attempted action is called (f.e., 'commenting')
            username (str): Account's username or email. If specified along with `password` a login attempt will
                            take place after the action
            password (str):
        """
        self._find_element_by_xpath(element_xpath).click()
        time.sleep(1)

        try:
            if username and password:
                self._find_element_by_xpath(NinegagXPaths.LoginPopup.LOGIN_LINK).click()
                self._login(username, password)
            else:
                self._find_element_by_xpath(NinegagXPaths.LoginPopup.CLOSE_BUTTON).click()
                raise AuthenticationRequired(f'{action_str.capitalize()} requires logging in')
        except NoSuchElementException:
            pass

    def scan_section(self, max_iterations: int):
        """
        Extract data from a sequence of posts and save it to DB
        Notes:
            * Assumes webdriver is in a section feed

        Args:
            max_iterations (int): Length of post sequence to extract, negative value will return an infinite generator

        Returns:
            generator of the posts collected
        """
        self._get(self._find_first_post())
        return self._scan_posts(max_iterations)

    def _find_first_post(self):
        """
        Finds the first non-board post in a feed
        Notes:
            * Assumes webdriver is in a section feed

        Returns:
            str: First post's url
        """
        for _ in range(MAX_ATTEMPTS_FOR_ACTION):

            first_article = self._find_nth_article(1)
            try:
                # If this is a board we ignore it
                first_article.find_element_by_xpath(NinegagXPaths.ARTICLE_OPEN_BOARD_RELATIVE)
                first_post = self._find_nth_article(2)
            except NoSuchElementException:
                first_post = first_article

            time.sleep(2)
            try:
                return first_post.find_element_by_xpath(NinegagXPaths.ARTICLE_LINK_RELATIVE).get_attribute('href')
            except StaleElementReferenceException:
                # Failure seems to be arbitrary, so we refresh and try again
                self._driver.refresh()
                continue

    def _find_nth_article(self, n: int):
        """
        Finds the article that appears at the n-th position in a feed
        Notes:
            * Currently does not supports high values for `n` as older articles are rendered only after scrolling
            * Assumes webdriver is in a section feed

        Args:
            n (int): The index of the article to fetch, starts from 1

        Returns:
            webdriver.WebElement: The article element
        """
        return self._find_element_by_xpath(f'//article[{n}]')

    def _scan_posts(self, iterations: int):
        """
        Extract data from a sequence of posts
        Notes:
            * Assumes webdriver is in a post page

        Args:
            iterations (int): Length of post sequence to extract

        Yields:
            NinegagPost: Representation of a post
        """
        count_sequence = itertools.count() if iterations < 0 else range(iterations)
        # There will be infinite iterations if specified -1 or smaller

        for _ in count_sequence:
            yield self._scan_post()
            self._next_post()

    def _scan_post(self):
        """
        Extracts useful data from a post
        Notes:
            * Assumes webdriver is in a post page

        Returns:
            NinegagPost: Representation of the current post
        """
        # We wait for the comments to be fully loaded, they are usually the last component to be rendered
        WebDriverWait(self._driver, MAX_DELAY).until(
            EC.presence_of_element_located((By.XPATH, NinegagXPaths.Post.COMMENT_SECTION_RENDER_CHECK)))
        return self.scan_post_from_html(self._driver.page_source, self._driver.current_url)

    def _next_post(self, wait_for_comments=True):
        """
        Press next-post button
        Notes:
            * Assumes webdriver is in a post page
        """
        self._find_element_by_xpath(NinegagXPaths.Post.NEXT_POST_BUTTON).click()

        # Waits for the post to render completely.
        # We must make sure that 'next-post' button is rendered, for assuring this function will work
        # as expected the next time it is being called
        WebDriverWait(self._driver, MAX_DELAY).until(
            EC.presence_of_element_located((By.XPATH, NinegagXPaths.Post.NEXT_POST_BUTTON)))

        if wait_for_comments:
            # Comments are usually rendered last and takes additional 0.5-2 seconds to load
            WebDriverWait(self._driver, MAX_DELAY).until(
                EC.presence_of_element_located((By.XPATH, NinegagXPaths.Post.COMMENT_SECTION_RENDER_CHECK)))
