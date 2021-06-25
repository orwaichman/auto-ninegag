WEBDRIVER_PATH = r'C:\OtherPrograms\geckodriver.exe'  # Be sure to install Geckodriver (or any other driver, just update the code accordingly)

NINEGAG_URL = "https://9gag.com"
NINEGAG_POST_URL_TEMPLATE = f"{NINEGAG_URL}/gag/{{post_id}}"
NINEGAG_IMAGE_URL_TEMPLATE = "https://img-9gag-fun.9cache.com/photo/{post_id}_700bwp.webp"


# There might be some work to do here in order to make the xpaths persist through 9GAG interface updates
class NinegagXPaths:
    SECTION_LIST = '//*[@id="container"]/div[1]/div/section/ul'  # Do not use xpath on its own, only with contain()
    SECTION_LIST_ITEM = f'{SECTION_LIST}/li/a'  # Do not use xpath on its own, only with contain()
    NIGHT_MODE_BUTTON = '//*[@id="top-nav"]/div/div/div[1]/a[1]'
    LOGIN_LINK = '//*[@id="top-nav"]/div/div/div[2]/a[1]'
    ARTICLE_LINK_RELATIVE = './/header/a'  # The nested <a> element is not clickable, we extract the href for get()
    ARTICLE_OPEN_BOARD_RELATIVE = './/a/div[contains(text(), "Open board")]'
    POST_JSON_SCRIPT = '/html/head/script[@type="application/ld+json"]'

    class LoginFrame:
        USERNAME_INPUT = '//*[@id="login-email-name"]'
        PASSWORD_INPUT = '//*[@id="login-email-password"]'
        SUBMIT_BUTTON = '//*[@id="login-email"]/div[3]/input'

    class Post:
        _ARTICLE = '//*[@id="individual-post"]/article'
        UPVOTE_BUTTON = f'{_ARTICLE}//div[contains(@class, "vote")]//a[contains(@class, "up")]'
        DOWNVOTE_BUTTON = f'{_ARTICLE}//div[contains(@class, "vote")]//a[contains(@class, "down")]'
        VOTE_LABEL_RELATIVE = './/span'
        NEXT_POST_BUTTON = f'{_ARTICLE}//a[contains(@class, "next")]'
        POST_TYPE_DIV = f'{_ARTICLE}//div[contains(@class, "post-container")]//a/div'
        SECTION_LABEL = f'{_ARTICLE}/header//div[contains(@class, "post-section")]//a[contains(@class, "section")]'
        TITLE = f'{_ARTICLE}/header/h1'

        _COMMENT_SECTION = '//section[contains(@class, "post-comment")]'
        COMMENT_COUNT_LABEL = f'{_COMMENT_SECTION}//header//span'
        COMMENT_SECTION_RENDER_CHECK = f'{_COMMENT_SECTION}//section[contains(@class, "comment-list")]//section'
            # Works either if there are comments or there are none

    class LoginPopup:
        CLOSE_BUTTON = '//*[@id="jsid-app"]/div/div[2]/section/a'
        LOGIN_LINK = '//*[@id="signup-fb"]/p[3]/a'
