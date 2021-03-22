import logging
import os
import time

from django.conf import settings
from selenium import webdriver

from mal2.utils import get_response


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# TAKE SCREENSHOT

def take_screenshot(website):
    if not os.path.exists(settings.SCREENSHOTS_PATH):
        os.makedirs(settings.SCREENSHOTS_PATH)

    name = "%s.png" % website.id
    screenshot = os.path.join(settings.SCREENSHOTS_PATH, name)

    if not os.path.exists(screenshot):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--window-size=1920,1080")
        # required if run as root user
        chrome_options.add_argument("--no-sandbox")

        response = get_response(website.url, method="get", headers={
            "User-Agent": "Mozilla/20.0.1 (compatible; MSIE 5.5; Windows NT)"
        })

        if not response:
            return False

        try:
            driver = webdriver.Chrome(options=chrome_options)

            driver.set_page_load_timeout(30)
            driver.get(website.url)

            time.sleep(2)

            driver.save_screenshot(screenshot)

            website.screenshot = name
            website.save()
        except Exception as error:  # noqa
            logger.debug(response)
            logger.error(error)
        finally:
            try:
                driver.quit()
            except UnboundLocalError as error:
                logger.error(error)

        return True
