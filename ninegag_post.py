from const import NINEGAG_POST_URL_TEMPLATE, NINEGAG_IMAGE_URL_TEMPLATE


class NinegagPost(object):

    def __init__(self,
                 post_id: str,
                 section: str,
                 title: str,
                 upvotes: int=None,
                 downvotes: int=None,
                 post_type=None,
                 comment_count=None,
                 publish_time=None,
                 fetch_time=None,
                 comments=None,
                 tags=None,
                 original_poster=None
                 ):
        self.post_id = post_id
        self.post_type = post_type
        self.section = section
        self.title = title
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.comment_count = comment_count
        self.publish_time = publish_time
        self.fetch_time = fetch_time
        self.comments = comments
        self.tags = tags
        self.original_poster = original_poster

    @property
    def url(self):
        return NINEGAG_POST_URL_TEMPLATE.format(post_id=self.post_id)

    @property
    def image_url(self):
        return NINEGAG_IMAGE_URL_TEMPLATE.format(post_id=self.post_id)

    @property
    def points(self):
        return self.upvotes - self.downvotes

    def __repr__(self):
        return f'<{self.__class__.__name__}(url={repr(self.url)})>'

    def __str__(self):
        return '\n '.join((f'Post #{self.post_id}',
                           f'post_type: {self.post_type}',
                           f'section: {self.section}',
                           f'title: {self.title}',
                           f'upvotes: {self.upvotes}',
                           f'downvotes: {self.downvotes}',
                           f'comment_count: {self.comment_count}',
                           f'publish_time: {self.publish_time}',
                           f'fetch_time: {self.fetch_time}',
                           f'url: {self.url}',
                           ))
