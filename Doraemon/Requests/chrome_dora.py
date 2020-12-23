# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.common.exceptions import TimeoutException
import logging


class MyChrome(webdriver.Chrome):
    def __init__(self, headless=False, proxy=None, no_images=False, user_agent=None, log_level=3):
        '''
        :param headless: headless or not
        :param proxy: e.g. 127.0.0.1:1080
        :param no_images: set True if you don't wanna load images, this option is time-saving
        '''
        chrome_options = webdriver.ChromeOptions()
        if proxy is not None:
            chrome_options.add_argument('--proxy-server={}'.format(proxy))
        if headless:
            chrome_options.add_argument("--headless")
        if no_images:
            prefs = {'profile.managed_default_content_settings.images': 2}
            chrome_options.add_experimental_option('prefs', prefs)
        if user_agent is not None:
            chrome_options.add_argument('--user-agent={}'.format(user_agent))
        chrome_options.add_argument("log-level={}".format(log_level))
        super(MyChrome, self).__init__(executable_path=ChromeDriverManager().install(),
                                       options=chrome_options)

    def wait_to_get_element(self, css_selector, timeout):
        while True:
            try:
                element = WebDriverWait(self, timeout).until(
                    ec.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
                break
            except Exception as e:
                print("page loading timeout! wait {} more seconds...".format(timeout))
                continue
        return element

    def screenshot_current_page(self, save_path):
        height = self.execute_script("return document.scrollingElement.scrollHeight;")
        width = self.execute_script("return document.scrollingElement.scrollWidth;")
        self.set_window_size(width, height)
        time.sleep(1)
        self.find_element_by_tag_name("body").screenshot(save_path)

    def get(self, *args, **kwargs):
        while True:
            try:
                res = super(MyChrome, self).get(*args, **kwargs)
                return res
            except TimeoutException as te:
                logging.warning("chrome.get timeout, retry again...")


if __name__ == "__main__":
    proxy = "127.0.0.1:1080"
    google_url = "https://www.google.com"
    baidu_url = "https://www.baidu.com"
    chrome = MyChrome(headless=True, proxy=proxy)
    chrome.get(google_url)
    print(chrome.page_source)