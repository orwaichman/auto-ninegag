import datetime
import itertools
import json
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from browser import Browser
from const import NINEGAG_URL, NinegagXPaths
from ninegag_post import NinegagPost
from exceptions import AuthenticationRequired, InvalidAction

MAX_DELAY = 10  # Seconds
MAX_ATTEMPTS_FOR_ACTION = 5


class NinegagBrowser(Browser):
    def _start(self, **options):
        """
        Opens a new WebDriver instance and browses to 9GAG homepage
        """
        super()._start(**options)
        self.driver.get(NINEGAG_URL)

    def go_to_section(self, section_name: str, fresh: bool = False):
        """
        Browse to a section URL
        Args:
            section_name (str): 9GAG section name as appears in the menu or in the URL, works with both
            fresh (bool): Whether to browse to section's Fresh (otherwise goes to Hot)
        """
        if section_name.lower() in ('hot', 'trending', 'fresh'):
            self.driver.get(f'{NINEGAG_URL}/{section_name.lower()}')
            return

        try:
            self.driver.find_element_by_xpath(NinegagXPaths.SECTION_LIST)
        except NoSuchElementException:
            raise NoSuchElementException('Could not find 9GAG menu, perhaps window is not wide enough')

        try:
            self.driver.find_element_by_xpath(
                f'{NinegagXPaths.SECTION_LIST_ITEM}[contains(text(), "{section_name}")]').click()
            return
        except NoSuchElementException:
            pass

        try:
            self.driver.find_element_by_xpath(f'{NinegagXPaths.SECTION_LIST_ITEM}[@href="/{section_name}"]')
            self.driver.get(f'{NINEGAG_URL}/{section_name}{"/fresh" if fresh else ""}')
            return
        except NoSuchElementException:
            raise InvalidAction(f'Section "{section_name}" was not found')

    def click_nightmode_button(self):
        """
        Turns night mode on or off
        """
        self.driver.find_element_by_xpath(NinegagXPaths.NIGHT_MODE_BUTTON).click()

    def login(self, username: str, password: str):
        """
        Authenticate to 9GAG
        Args:
            username (str): Account's username or email
            password (str): Account's password
        """
        self.driver.find_element_by_xpath(NinegagXPaths.LOGIN_LINK).click()
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
        username_input = WebDriverWait(self.driver, MAX_DELAY).until(
            EC.presence_of_element_located((By.XPATH, NinegagXPaths.LoginFrame.USERNAME_INPUT)))
        username_input.send_keys(username)

        self.driver.find_element_by_xpath(NinegagXPaths.LoginFrame.PASSWORD_INPUT).send_keys(password)

        self.driver.find_element_by_xpath(NinegagXPaths.LoginFrame.SUBMIT_BUTTON).click()

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
        self.driver.find_element_by_xpath(element_xpath).click()
        time.sleep(1)

        try:
            if username and password:
                self.driver.find_element_by_xpath(NinegagXPaths.LoginPopup.LOGIN_LINK).click()
                self._login(username, password)
            else:
                self.driver.find_element_by_xpath(NinegagXPaths.LoginPopup.CLOSE_BUTTON).click()
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
        self.driver.get(self._find_first_post())
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
                self.driver.refresh()
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
        return self.driver.find_element_by_xpath(f'//article[{n}]')

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
            db.models.NinegagPost: Representation of the current post
        """
        post_id = self.driver.current_url.split("/")[-1]

        post_classes = set(
            self.driver.find_element_by_xpath(NinegagXPaths.Post.POST_TYPE_DIV).get_attribute('class').split())
        post_classes.remove('post-view')
        post_type = post_classes.pop().replace('-post', '')

        section = self.driver.find_element_by_xpath(NinegagXPaths.Post.SECTION_LABEL).text

        title = self.driver.find_element_by_xpath(NinegagXPaths.Post.TITLE).text

        upvote_button = self.driver.find_element_by_xpath(NinegagXPaths.Post.UPVOTE_BUTTON)
        upvotes = self._numeric_label_to_int(
            upvote_button.find_element_by_xpath(NinegagXPaths.Post.VOTE_LABEL_RELATIVE).text)
        downvote_button = self.driver.find_element_by_xpath(NinegagXPaths.Post.DOWNVOTE_BUTTON)
        downvotes = self._numeric_label_to_int(
            downvote_button.find_element_by_xpath(NinegagXPaths.Post.VOTE_LABEL_RELATIVE).text)

        comments_label = self.driver.find_element_by_xpath(NinegagXPaths.Post.COMMENT_COUNT_LABEL).text
        comment_count = self._numeric_comments_label_to_int(comments_label)

        page_json = self.driver.find_element_by_xpath(NinegagXPaths.POST_JSON_SCRIPT).get_attribute('innerHTML')
        post_info = json.loads(page_json)
        publish_time = datetime.datetime.strptime(post_info['datePublished'], "%Y-%m-%dT%H:%M:%S%z")

        fetch_time = datetime.datetime.now()

        return NinegagPost(post_id=post_id,
                           post_type=post_type,
                           section=section,
                           title=title,
                           upvotes=upvotes,
                           downvotes=downvotes,
                           comment_count=comment_count,
                           publish_time=publish_time,
                           fetch_time=fetch_time
                           )

    def _next_post(self):
        """
        Press next-post button
        Notes:
            * Assumes webdriver is in a post page
        """
        self.driver.find_element_by_xpath(NinegagXPaths.Post.NEXT_POST_BUTTON).click()

        # Waits for the post to render completely.
        # We must make sure that 'next-post' button is rendered, for assuring this function will work
        # as expected the next time is is being called
        WebDriverWait(self.driver, MAX_DELAY).until(
            EC.presence_of_element_located((By.XPATH, NinegagXPaths.Post.NEXT_POST_BUTTON)))
        # We also wait for the comments to be fully loaded, as they are usually the last component to be rendered
        WebDriverWait(self.driver, MAX_DELAY).until(
            EC.presence_of_element_located((By.XPATH, NinegagXPaths.Post.COMMENT_SECTION_RENDER_CHECK)))

    @staticmethod
    def _numeric_label_to_int(label):
        """
        Convert text (from 9gag site) that represent numerical value to int
        Args:
            label (str): Integer represented as string

        Returns:
            int: The integer in the string or -1 if the string was not a valid number
        """
        try:
            return int(label)  # A pure numerical
        except ValueError:
            pass

        if 'k' in label:
            return int(float(label.split('k')[0]) * 1000)  # numerical greater than 999 is represented as '1.1k'
        else:
            return -1  # A hour has not passed since the post was published so no count appears

    @staticmethod
    def _numeric_comments_label_to_int(label):
        """
        Convert comment count text (from 9gag site) to int
        Args:
            label (str): comment count label

        Returns:
            int: The integer in the string or 0 if there was no number specified
        """
        count = label.replace('Comments', '')
        if not count:
            return 0
        return int(count)
