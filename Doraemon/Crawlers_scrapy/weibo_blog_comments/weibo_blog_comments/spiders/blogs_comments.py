import scrapy
import json
from datetime import datetime
import time
import re

class BlogsCommentsSpider(scrapy.Spider):
    name = 'blogs_comments'

    def start_requests(self):
        show2uid2name = {
            "半熟恋人": {
                "2118184942": "周楠",
                "1986980987": "杨梦婧",
                "5915414924": "罗颖",
                "6188115154": "罗拉",
                "1824090235": "童瑶",
                "5628475354": "黄瑞恩",
                "5384721358": "俞悦",
                "1880171790": "周锦舜",
                "1814194933": "王能能",
                "7704087868": "王雨城",
            }
        }
        show2starttime = {
            "半熟恋人": "2021 12 28 19:00:00"
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            "cookie": "_T_WM=26818157195; SUB=_2A25OEyLTDeRhGeFJ61YR-CnEzTSIHXVt_E6brDV6PUJbktAKLWTNkW1NfKbZ-kxPhfMQdYW3bqYnON-180fYkl7a; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFMOSlN8oDRwUroYf4GTYxo5NHD95QNS05XehnN1hqRWs4Dqcjki--NiKy8iKyFi--4iKLFi-2Ri--fiKLsiKy8Bg4.wBtt; SSOLoginState=1662472835; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D20000174%26lfid%3D1076037704087868",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        }

        for show, uid2name in show2uid2name.items():
            for uid, name in uid2name:
                blogs_url = "https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid=107603{}&page=1".format(uid, uid)
                yield scrapy.Request(url=blogs_url, headers=headers, callback=self.parse, meta={"start_time": show2starttime[show], "page": 1})

    # def parse_blog_list(self, response):
    #     res_dict = json.loads(response.text)
    #
    #     time_str_map = {
    #         "Jan": "01",
    #         "Feb": "02",
    #         "Mar": "03",
    #         "Apr": "04",
    #         "May": "05",
    #         "Jun": "06",
    #         "Jul": "07",
    #         "Aug": "08",
    #         "Sept": "09",
    #         "Sep": "09",
    #         "Oct": "10",
    #         "Nov": "11",
    #         "Dec": "12",
    #     }
    #     time_pattern = "%Y %m %d %H:%M:%S"
    #     start_time = datetime.strptime(response.meta["start_time"], time_pattern).timestamp()
    #
    #     while res_dict["ok"] == 1:
    #         time_break = False
    #         for card in res_dict["data"]["cards"]:
    #             if card["card_type"] != 9:
    #                 continue
    #
    #             # creating time
    #             time_str = card["mblog"]["created_at"]
    #             t_split = time_str.split()
    #             t_str_normal = "{} {} {} {}".format(t_split[-1], time_str_map[t_split[1]], t_split[2], t_split[3])
    #             timestamp = datetime.strptime(t_str_normal, time_pattern).timestamp()
    #             if timestamp < start_time:
    #                 time_break = True
    #                 break
    #
    #
    #             if ">全文</a>" in card["mblog"]["text"]:
    #                 while True:
    #                     try:
    #                         status_url = "https://m.weibo.cn/status/{}".format(card["mblog"]["mid"])
    #                         res = mweibo_session.get(status_url, headers=headers)
    #                         status_js_txt = re.search("var \$render_data = \[(.*)\]\[0\] \|\| \{\};", res.text,
    #                                                   flags=re.DOTALL).group(1)
    #                         res_dict = json.loads(status_js_txt)["status"]
    #                         blog_list.append(res_dict)
    #                         break
    #                     except Exception as e:
    #                         logging.warning("post {} status 失败，重试".format(card["mblog"]["mid"]))
    #                         pass
    #             else:
    #                 blog_list.append(card["mblog"])
    #             mid_set.add(card["mblog"]["mid"])
    #
    #         if time_break:
    #             break
    #
    #         print("blog_list: {}".format(len(blog_list)))
    #         time.sleep(1)
    #         page += 1
    #         res_dict = get_blogs(page)
    #
    # def get_long_text(self, response):

