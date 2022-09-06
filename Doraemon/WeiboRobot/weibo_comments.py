import json
import logging
import time

import requests
from tqdm import tqdm
from datetime import datetime
from DecryptLogin import login

headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        "x-xsrf-token": "ca8f34",
        "cookie": "_T_WM=95408813990; XSRF-TOKEN=ca8f34; SCF=AvAoiM-KriYpOE7doKShZInAbXDWWZNF2LALSnsH7OKum4ytQ30c_ymO7WpHP1Zt4EOkNaeFawbBlpQjRPQ4yoM.; SUB=_2A25Pa7GDDeRhGeFJ61YR-CnEzTSIHXVsl9_LrDV6PUJbktCOLXbNkW1NfKbZ-gLFw-TULujLZsmu8bvgIK35TFs1; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFMOSlN8oDRwUroYf4GTYxo5NHD95QNS05XehnN1hqRWs4Dqcjki--NiKy8iKyFi--4iKLFi-2Ri--fiKLsiKy8Bg4.wBtt; WEIBOCN_FROM=1110006030; MLOGIN=1; SSOLoginState=1651491369; M_WEIBOCN_PARAMS=lfid=102803&luicode=20000174&uicode=20000174; mweibo_short_token=7674ff4669",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
}
# 设置一个会话
mweibo_session = requests.Session()


client = login.Client()
weibo = client.weibo(reload_history=True)
infos_return, weibo_session = weibo.login('13120178370', 'Weibo6981228.', mode='scanqr')


def get_all_blogs(uid, start_time="2021 12 28 19:00:00"):
    def get_blogs(since_id=None):
        blogs_url = "https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid=107603{}".format(uid, uid)
        if since_id:
            blogs_url += "&since_id=" + since_id

        while True:
            try:
                res = mweibo_session.get(blogs_url, headers=headers)
                res_dict = json.loads(res.text)
                break
            except Exception as e:
                logging.warning("获取微博id失败，重试")
                pass

        return res_dict

    res_dict = get_blogs(None)

    blog_list = []
    mid_set = set()
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
    start_time = datetime.strptime(start_time, time_pattern).timestamp()

    while res_dict["ok"] == 1 and len(blog_list) < res_dict["data"]["cardlistInfo"]["total"]:
        time_break = False
        for card in res_dict["data"]["cards"]:
            if card["card_type"] != 9:
                continue

            # creating time
            time_str = card["mblog"]["created_at"]
            t_split = time_str.split()
            t_str_normal = "{} {} {} {}".format(t_split[-1], time_str_map[t_split[1]], t_split[2], t_split[3])
            timestamp = datetime.strptime(t_str_normal, time_pattern).timestamp()
            if timestamp < start_time:
                time_break = True
                break

            if card["mblog"]["mid"] not in mid_set:
                blog_list.append(card["mblog"])
                mid_set.add(card["mblog"]["mid"])

        if time_break:
            break

        print("blog_list: {}".format(len(blog_list)))
        time.sleep(1)
        res_dict = get_blogs(blog_list[-1]["mid"])

    return blog_list


def get_comments_data(uid, mid):
    batch_size = 200
    comments_url = "https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id={}&is_show_bulletin=2&is_mix=0&count={}&uid={}".format(mid, batch_size, uid)

    while True:
        try:
            res = weibo_session.get(comments_url)
            res_dict = json.loads(res.text)
            if res_dict["ok"] == 1:
                break
        except Exception as e:
            logging.warning("获取评论失败，重试")
            pass

    comments_data = []
    comments_data.extend(res_dict["data"])

    while res_dict["max_id"] != 0:
        comments_url = "https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id={}&is_show_bulletin=2&is_mix=0&max_id={}&count={}&uid={}".format(
            mid, res_dict["max_id"], batch_size, uid)
        while True:
            try:
                res = weibo_session.get(comments_url)
                res_dict = json.loads(res.text)
                if res_dict["ok"] == 1:
                    break
            except Exception as e:
                logging.warning("获取评论失败，重试")
                pass

        if len(res_dict["data"]) > 0:
            comments_data.extend(res_dict["data"])
        elif res_dict["trendsText"] == "已加载全部评论":
            break

    return comments_data


def reply_statistics(uid, ignored_uids):
    blog_list = get_all_blogs(uid)
    uid2count_name = {}
    for idx, blog in enumerate(tqdm(blog_list)):
        all_comments_data = get_comments_data(uid, blog["mid"])

        for comment in all_comments_data:
            if comment["user"]["idstr"] not in ignored_uids:
                uid2count_name.setdefault(comment["user"]["idstr"],
                                          {"re_count": 0, "cmt_count": 0, "names": set()})
                uid2count_name[comment["user"]["idstr"]]["cmt_count"] += 1
                uid2count_name[comment["user"]["idstr"]]["names"].add(comment["user"]["name"])

            if "comments" in comment and len(comment["comments"]) > 0:
                for c in comment["comments"]:  # 翻牌只可能在评论的评论里
                    if c["user"]["idstr"] == uid:  # 如果是博主本人的回复即为翻牌
                        reply_comment = c["reply_comment"] if "reply_comment" in c and "user" in c["reply_comment"] else comment
                        if reply_comment["user"]["idstr"] not in ignored_uids:
                            uid2count_name.setdefault(reply_comment["user"]["idstr"], {"re_count": 0, "cmt_count": 0, "names": set()})
                            uid2count_name[reply_comment["user"]["idstr"]]["re_count"] += 1
                            uid2count_name[reply_comment["user"]["idstr"]]["names"].add(reply_comment["user"]["name"])

    uid2re_count_name = dict(sorted(uid2count_name.items(), key=lambda x: x[1]["re_count"], reverse=True))
    uid2cmt_count_name = dict(sorted(uid2count_name.items(), key=lambda x: x[1]["cmt_count"], reverse=True))
    return uid2re_count_name, uid2cmt_count_name


if __name__ == "__main__":
    uid2name = {
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
    uid2statistics = {}

    for uid in uid2name.keys():
        uid2re_count_name, uid2cmt_count_name = reply_statistics(uid, uid2name.keys())
        uid2statistics[uid2name[uid]] = {"comment": uid2cmt_count_name, "reply": uid2re_count_name}


