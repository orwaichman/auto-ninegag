# auto-ninegag
Auto-Ninegag is a tool consists of programmatic implementation of actions that can be done in 9gag.com website via web browser.


## Disclaimers
The library was planned to be expandible and at the moment supports only a small set of actions.
Notice that 9GAG is not supportive of using bots (at least compared to the bot-friendly Reddit) and we take no responsibilty for any misuse of this code. In fact, the use of Selenium is necessary to perform actions on 9GAG site as simply using requests module is not enough to overcome 9GAG's Captcha.
This project is not planned to be maintained in a level that it could persist 9gag frequent UI updates, and is not reliable for any worthy use.

## Pre-use preperations
* Set-up a webdriver (for Selenium):
    * Make sure Firefox is installed
    * Download Geckodriver
    * Update _WEBDRIVER_PATH_ in const.py
    * Notice that you can use a non-firefox web driver for your choosing, but make sure to update the code accordingly.
