from ninegag_browser import NinegagBrowser
from const import WEBDRIVER_PATH


def main():
    # Example of usage
    with NinegagBrowser(executable_path=WEBDRIVER_PATH) as ninegag_browser:
        ninegag_browser.go_to_section('Funny')
        posts_scanned = ninegag_browser.scan_section(max_iterations=16)
        print('\n\n'.join([str(item) for item in posts_scanned]))


if __name__ == '__main__':
    main()
