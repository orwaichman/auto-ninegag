import datetime
import json

from lxml import html

from basic_browser import BasicBrowser
from const import NinegagXPaths
from ninegag_post import NinegagPost


class NinegagBasicBrowser(BasicBrowser):
    @staticmethod
    def scan_post_from_html(page_html, url=None):
        """
        Extracts data from a fully loaded html page of a 9GAG post
        Args:
            page_html (str): 9GAG post page
            url: Page's url, optional

        Returns:
            NinegagPost:
        """
        if not isinstance(page_html, html.HtmlElement):
            page_html = html.fromstring(page_html)

        if url:
            post_id = url.split("/")[-1]
        else:
            post_id = page_html.xpath(NinegagXPaths.Post.URL_META)[0].split("/")[-1]

        post_classes = set(
            page_html.xpath(NinegagXPaths.Post.POST_TYPE_DIV)[0].attrib['class'].split())
        post_classes.remove('post-view')
        post_type = post_classes.pop().replace('-post', '')

        section = page_html.xpath(NinegagXPaths.Post.SECTION_LABEL)[0].text

        title = page_html.xpath(NinegagXPaths.Post.TITLE)[0].text

        upvote_button = page_html.xpath(NinegagXPaths.Post.UPVOTE_BUTTON)[0]
        upvotes = NinegagBasicBrowser._numeric_label_to_int(
            upvote_button.xpath(NinegagXPaths.Post.VOTE_LABEL_RELATIVE)[0].text)
        downvote_button = page_html.xpath(NinegagXPaths.Post.DOWNVOTE_BUTTON)[0]
        downvotes = NinegagBasicBrowser._numeric_label_to_int(
            downvote_button.xpath(NinegagXPaths.Post.VOTE_LABEL_RELATIVE)[0].text)

        comments_label = page_html.xpath(NinegagXPaths.Post.COMMENT_COUNT_LABEL)[0].text
        comment_count = NinegagBasicBrowser._numeric_comments_label_to_int(comments_label)

        page_json = page_html.xpath(NinegagXPaths.POST_JSON_SCRIPT)[0].text_content()
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
