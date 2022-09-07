import scrapy
import json
from datetime import datetime
import re
from DecryptLogin import login


class BlogsCommentsSpider(scrapy.Spider):
    name = 'blogs_comments'

    def __init__(self):
        super(BlogsCommentsSpider, self).__init__()
        client = login.Client()
        weibo = client.weibo(reload_history=True)
        _, self.weibo_session = weibo.login('13120178370', 'Weibo6981228.', mode='scanqr')

    def get_mweibo_headers(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            "cookie": "_T_WM=26818157195; SUB=_2A25OEyLTDeRhGeFJ61YR-CnEzTSIHXVt_E6brDV6PUJbktAKLWTNkW1NfKbZ-kxPhfMQdYW3bqYnON-180fYkl7a; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFMOSlN8oDRwUroYf4GTYxo5NHD95QNS05XehnN1hqRWs4Dqcjki--NiKy8iKyFi--4iKLFi-2Ri--fiKLsiKy8Bg4.wBtt; SSOLoginState=1662472835; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D20000174%26lfid%3D1076037704087868",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        }
        return headers

    def start_requests(self):
        show2uid2name = {
            "半熟恋人": {
                # "2118184942": "周楠",
                # "1986980987": "杨梦婧",
                # "5915414924": "罗颖",
                # "6188115154": "罗拉",
                # "1824090235": "童瑶",
                # "5628475354": "黄瑞恩",
                # "5384721358": "俞悦",
                # "1880171790": "周锦舜",
                # "1814194933": "王能能",
                "7704087868": "王雨城",
            }
        }

        for show, uid2name in show2uid2name.items():
            for uid, name in uid2name.items():
                blogs_url = "https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid=107603{}&page=1".format(uid, uid)
                yield scrapy.Request(url=blogs_url, headers=self.get_mweibo_headers(), callback=self.parse_blog_list, meta={"uid": uid,
                    "show": show,
                                                                                                                  "page": 1})

    def parse_blog_list(self, response):
        res_dict = json.loads(response.text)
        if res_dict["ok"] != 1:
            return
        uid = response.meta["uid"]
        time_str_map = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sept": "09",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }
        time_pattern = "%Y %m %d %H:%M:%S"
        show2starttime = {
            "半熟恋人": "2021 12 28 19:00:00"
        }
        start_time = datetime.strptime(show2starttime[response.meta["show"]], time_pattern).timestamp()

        for card in res_dict["data"]["cards"]:
            if card["card_type"] != 9:
                continue

            # creating time
            time_str = card["mblog"]["created_at"]
            t_split = time_str.split()
            t_str_normal = "{} {} {} {}".format(t_split[-1], time_str_map[t_split[1]], t_split[2], t_split[3])
            timestamp = datetime.strptime(t_str_normal, time_pattern).timestamp()
            if timestamp < start_time:
                break

            mid = card["mblog"]["mid"]
            # get comments
            comments_url = "https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id={}&is_show_bulletin=2&is_mix=0&count={}&uid={}".format(
                mid, 200, uid)
            yield scrapy.Request(url=comments_url, callback=self.parse_comments,
                                 meta={"uid": uid, "mid": mid, "cookiejar": self.weibo_session})

            if ">全文</a>" in card["mblog"]["text"]:
                status_url = "https://m.weibo.cn/status/{}".format(card["mblog"]["mid"])
                yield scrapy.Request(url=status_url, headers=self.get_mweibo_headers(), callback=self.parse_long_text,
                                 meta={"uid": uid, "mid": mid})
            else:
                # yield blogs
                card["mblog"]["item_type"] = "blog"
                yield card["mblog"]


        # next page
        page = response.meta["page"] + 1
        blogs_url = "https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid=107603{}&page={}".format(
            uid, uid, page)
        yield scrapy.Request(url=blogs_url, headers=self.get_mweibo_headers(), callback=self.parse_blog_list, meta={"show": response.meta["show"],
                                                                                                          "uid": uid, "page": page})

    def parse_comments(self, response):
        res_dict = json.loads(response.text)
        if res_dict["ok"] != 1:
            return

        uid, mid = response.meta["uid"], response.meta["mid"]
        if len(res_dict["data"]) > 0:
            yield {
                "item_type": "comm",
                "uid": uid,
                "mid": mid,
                "data": res_dict["data"]
            }
        elif res_dict["trendsText"] == "已加载全部评论":
            return

        if res_dict["max_id"] != 0:
            comments_url = "https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id={}&is_show_bulletin=2&is_mix=0&max_id={}&count={}&uid={}".format(
                mid, res_dict["max_id"], 200, uid)
            yield scrapy.Request(url=comments_url, callback=self.parse_comments,
                                 meta={"uid": uid, "mid": mid, "cookiejar": self.weibo_session})

    def parse_long_text(self, response):
        status_js_txt = re.search("var \$render_data = \[(.*)\]\[0\] \|\| \{\};", response.text,
                                  flags=re.DOTALL).group(1)
        blog_status = json.loads(status_js_txt)["status"]
        blog_status["item_type"] = "blog"
        yield blog_status



