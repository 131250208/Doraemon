import time
import base64
from Doraemon.Others import ext_apis
from Doraemon.Requests import chrome_dora
import os
from tqdm import tqdm
import logging
from pprint import pprint


class OrgInvestigator:
    def __init__(self, api_key):
        self.url_map = {
            "baidu": "https://www.baidu.com/s?&wd={}&ie=utf-8",
            "neris": "http://neris.csrc.gov.cn/shixinchaxun/",
            "mee_gov": "http://www.mee.gov.cn/qwjs2019/?searchword={}",
            "mnr_gov": "http://s.lrn.cn/jsearchfront/search.do?" +
                  "websiteid=110000000000000&pg=1&p=1&searchid=1&tpl=13&cateid=1&q={}" +
                  "&filter=001&x=0&y=0",
            "china_tax": "http://www.chinatax.gov.cn/s?qt={}&siteCode=bm29000002&tab=all&toolsStatus=1",
            "zxgk": "http://zxgk.court.gov.cn/zhzxgk/",
            # "customs": "http://www.customs.gov.cn"
        }
        self.name_map = {
            "baidu": "百度检索结果",
            "neris": "中国证监会证券期货市场失信检索结果",
            "mee_gov": "中华人民共和国生态环境部检索结果",
            "mnr_gov": "中华人民共和国自然资源部检索结果",
            "china_tax": "国家税务局重大税收违法案件信息公布栏检索结果",
            "zxgk": "全国法院被执行人信息检索结果",
            # "customs": "中国海关总署检索结果",
        }

        # for websites need to recognize captcha
        self.ele_map = {
            "neris": {
                "captcha": "img#captcha_img",
                "captcha_inp": "input#ycode",
                "org": "input#objName",
                "submit": "img#querybtn",
                "info": "td.search_bg",
            },
            "zxgk": {
                "captcha": "img#captchaImg",
                "captcha_inp": "input#yzm",
                "org": "input#pName",
                "submit": 'div#yzm-group button[onclick*="search();"]',
                "info": "div#yzm-group",
            }
        }

        # init chrome
        user_ag = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        self.chrome = chrome_dora.MyChrome(headless=True, proxy=None, user_agent=user_ag)
        # filter
        self.api_key = api_key

    def investigate(self,
                    key_word_list,
                    save_dir,
                    switch
                    ):
        switch_ = {key: val for key, val in switch.items() if val is True}
        captcha_error_info = {}
        for key_word in key_word_list:
            for website, val in tqdm(switch_.items(), desc="screenshot {}".format(key_word)):
                if val:
                    url = self.url_map[website]
                    web_name = self.name_map[website]
                    if website not in {"neris", "zxgk", "customs"}:
                        url = url.format(key_word)
                        self.chrome.get(url)
                    # elif website == "customs":
                    #     self.chrome.get(url)
                    #     inp_box = self.chrome.find_element_by_css_selector("input#ess_ctr151088_ListC_Info_ctl00_KEYWORDS")
                    #     inp_box.send_keys(key_word)
                    #     inp_box.send_keys(Keys.ENTER)

                    else:
                        elements = self.ele_map[website]
                        self.chrome.get(url)

                        def refresh():
                            while True:
                                self.chrome.refresh()
                                time.sleep(1)
                                body_text = self.chrome.find_element_by_tag_name("body").text
                                if "找不到您要的页面" not in body_text:
                                    break
                        # screen_shot captcha and recognize it
                        # self.chrome.wait_to_get_element(elements["captcha"], 5)

                        def input_kw_n_captch():
                            # input organization name
                            refresh()
                            self.chrome.find_element_by_css_selector(elements["org"]).send_keys(key_word)
                            time.sleep(0.5)
                            captcha_inp = self.chrome.find_element_by_css_selector(elements["captcha_inp"])
                            captcha_inp.click()

                            self.chrome.find_element_by_css_selector(elements["captcha"]).screenshot('{}/captcha.png'.format(save_dir))
                            captcha_bin = open("{}/captcha.png".format(save_dir), "rb").read()
                            captcha_bs64 = base64.b64encode(captcha_bin).decode()
                            captcha_code = ext_apis.captcha_rec_3023data(captcha_bs64,
                                                                         format="png",
                                                                         type=5001,
                                                                         api_key=self.api_key)
                            # input captcha code
                            captcha_inp.send_keys(captcha_code)
                            # click to submit
                            self.chrome.find_element_by_css_selector(elements["submit"]).click()
                            time.sleep(1)

                        input_kw_n_captch()
                        while True:
                            body_text = self.chrome.find_element_by_tag_name("body").text
                            if "验证码错误" in body_text:
                                logging.warning("验证码错误，正在重试...".format())
                                # log error num
                                if key_word not in captcha_error_info:
                                    captcha_error_info[key_word] = {}
                                captcha_error_info[key_word][web_name] = captcha_error_info[key_word].get(web_name, 0) + 1
                                input_kw_n_captch()
                            else:
                                break

                    save_path = os.path.join(save_dir, web_name)
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)
                    save_path = os.path.join(save_path, "{}.png".format(key_word))
                    self.chrome.screenshot_current_page(save_path)

        if len(captcha_error_info) > 0:
            print("本轮检索累积验证码错误次数统计如下，注意检查账户余额。")
            pprint(captcha_error_info)

    def quite(self):
        # quit
        self.chrome.quit()


if __name__ == "__main__":
    key_word_list = ["山东华骜植化", "华泰证券", "广发证券", "海通证券"]
    api_key = "7dab451889b5f88db606750d615d9824"
    save_dir = "./temp"
    switch = {
        "baidu": True,
        "neris": True,
        "mee_gov": True,
        "mnr_gov": True,
        "china_tax": True,
        "zxgk": True,
        # "customs": True,
    }
    investigator = OrgInvestigator(api_key)
    investigator.investigate(key_word_list, save_dir, switch)
