from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


class MyChrome(webdriver.Chrome):
    def __init__(self, headless=False, proxy=None, no_images=True):
        '''
        :param headless: headless or not
        :param proxy: e.g. 127.0.0.1:1080
        :param no_images: set True if you don't wanna load images, this option is time-saving
        '''
        chrome_options = webdriver.ChromeOptions()
        if proxy is not None:
            chrome_options.add_argument('--proxy-server=%s' % proxy)
        if headless:
            chrome_options.add_argument("--headless")
        if no_images:
            prefs = {'profile.managed_default_content_settings.images': 2}
            chrome_options.add_experimental_option('prefs', prefs)
        super(MyChrome, self).__init__(options=chrome_options)

    def wait_to_get_element(self, css_selector, timeout):
        while True:
            try:
                element = WebDriverWait(self, timeout).until(
                    ec.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
                break
            except Exception as e:
                print(e)
                continue
        return element

if __name__ == "__main__":
    proxy = "127.0.0.1:1080"
    google_url = "https://www.google.com"
    baidu_url = "https://www.baidu.com"
    chrome = MyChrome(headless=True, proxy=proxy)
    chrome.get(google_url)
    print(chrome.page_source)