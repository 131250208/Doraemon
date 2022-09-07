# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class WeiboBlogCommentsSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


import requests
import threading, time
import json
import random


class WeiboBlogCommentsDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    # def __init__(self):
    #     super(WeiboBlogCommentsDownloaderMiddleware, self).__init__()
    #
    #     self.proxies = []
    #
    #     # thread: updating
    #     def upd_proxy():
    #         count = 0
    #         while True:
    #             res = self.ext_proxies()
    #             if res is True:
    #                 count += 1
    #             time.sleep(14)
    #             if count % 4 == 0:
    #                 self.proxies = self.proxies[10:]
    #     t = threading.Thread(target=upd_proxy, name='LoopThread')
    #     t.start()
    #     # t.join()

    # def ext_proxies(self):
    #     url = "https://proxyapi.horocn.com/api/v2/proxies?order_id=AZZN1743303529091623&num=10&format=json&line_separator=win&can_repeat=no&user_token=ad054b709ea6e1fa2a9c5bcd081483c9"
    #     res = requests.get(url)
    #     res_js = json.loads(res.text)
    #     if res_js["code"] == 0 and res_js["msg"] == "OK":
    #         self.proxies.extend(["{}:{}".format(p["host"], p["port"])
    #                              for p in res_js["data"]])
    #         return True
    #     else:
    #         return False
    #
    # def get_proxy(self):
    #     if len(self.proxies) == 0:
    #         self.ext_proxies()
    #     return random.choice(self.proxies)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # if len(spider.proxies) == 0:
        #     self.ext_proxies(spider.proxies)
        #
        # proxy = random.choice(spider.proxies)
        # request.meta["proxy"] = "http://{}".format(proxy)
        # print(f"TestProxyMiddleware --> {proxy}")

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.proxies = []

        # thread: updating
        # def upd_proxy():
        #     count = 0
        #     while True:
        #         res = self.ext_proxies(spider.proxies)
        #         if res is True:
        #             count += 1
        #         time.sleep(14)
        #         if count % 4 == 0:
        #             spider.proxies = spider.proxies[10:]
        # spider.proxy_thread = threading.Thread(target=upd_proxy, name='LoopThread')
        # spider.proxy_thread.setDaemon(True)
        # spider.proxy_thread.start()

        # t.join()as
        spider.logger.info('Spider opened: %s' % spider.name)

    def ext_proxies(self, proxies):
        url = "https://proxyapi.horocn.com/api/v2/proxies?order_id=AZZN1743303529091623&num=10&format=json&line_separator=win&can_repeat=no&user_token=ad054b709ea6e1fa2a9c5bcd081483c9"
        res = requests.get(url)
        res_js = json.loads(res.text)
        if res_js["code"] == 0 and res_js["msg"] == "OK":
            proxies.extend(["{}:{}".format(p["host"], p["port"])
                                 for p in res_js["data"]])
            return True
        else:
            return False
