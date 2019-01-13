from Doraemon import requests_dora
from bs4 import BeautifulSoup
import re
import time
import logging
import random


def get_around(city_id, shop_id_center, dis, page, get_proxies_fun=None):
    '''
    get shops in the vicinity of the center shop
    :param city_id: the id of the target city
    :param shop_id_center: shop id of the center shop
    :param dis: the max distance of shops from the center shop
    :param page: page index [1, 50]
    :return: a list of shops
    e.g.
    [
      {
        "img_src": "https://img.meituan.net/msmerchant/2e5787325ba4579ec2e2e3f45038ade1149446.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D1%26%26r%3D1%26p%3D9%26x%3D2%26y%3D2%26relative%3D1%26o%3D20",
        "title": "速度披萨(华贸城店)",
        "star_level": 4.5,
        "review_num": 30,
        "mean_price": 89,
        "cat": "西餐",
        "region": "北苑家园",
        "addr": "清苑路13号",
        "rec_dish": [
          "黑芝麻沙拉",
          "蟹肉意面",
          "火腿榴莲披萨双拼"
        ],
        "score": {
          "taste": 8.5,
          "env": 8.4,
          "service": 8.4
        }
      },
    ]
    '''

    url = "http://www.dianping.com/search/around/{}/10_{}/d{}p{}".format(city_id, shop_id_center, dis, page)
    headers = requests_dora.get_default_headers()
    headers["Accept"] = 'application/json, text/javascript'
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    headers["Host"] = "www.dianping.com"
    del headers["Referer"]

    while True:
        res = requests_dora.try_best_2_get(url, get_proxies_fun=get_proxies_fun, headers=headers)
        if res.status_code == 200:
            break
        random.seed(time.time())
        sleep_time = 3 + 7 * random.random()
        logging.warning("failde ... try again in {} s...".format(sleep_time))
        time.sleep(sleep_time)

    # decrypt
    html = res.text
    if "没有找到" in html:
        logging.warning("can not find any shops...")
        return None
    
    url = "https:{}".format(re.search('href="(//s3plus\.meituan\.net.*?\.css)">', html).group(1))
    map_code2char = get_map_code2char(url)
    it = re.finditer('<span class="([0-9a-zA-Z]*?)"></span>', html)
    for match in it:
        code = match.group(1)
        if code in map_code2char:
            html = re.sub('<span class="{}"></span>'.format(code), map_code2char[code], html)

    soup = BeautifulSoup(html, "lxml")
    li_list = soup.select("div.shop-list > ul > li")

    # crawl
    shop_list = []
    for li in li_list:
        shop = {}
        try:
            img = li.select_one("div.pic img")
            img_src = img["src"]
            shop["img_src"] = img_src
        except:
            pass

        try:
            txt = li.select_one("div.txt")
            title = txt.select_one("div.tit > a")["title"]
            shop["title"] = title
        except:
            continue

        try:
            comment = txt.select_one("div.comment")
            star_span = str(comment.select_one("span.sml-rank-stars"))
            star_level = float(re.search("sml-str(\d+)", star_span).group(1)) / 10
            shop["star_level"] = star_level
            review_num = int(comment.select_one("a.review-num > b").get_text())
            shop["review_num"] = review_num
            mean_price = comment.select_one("a.mean-price > b").get_text()
            mean_price = int(re.search("(\d+)", mean_price).group(1))
            shop["mean_price"] = mean_price
        except:
            pass

        try:
            tag_addr = txt.select_one("div.tag-addr")
            category = tag_addr.select_one('a[data-click-name="shop_tag_cate_click"] > span.tag').get_text()
            region = tag_addr.select_one('a[data-click-name="shop_tag_region_click"] > span.tag').get_text()
            addr = tag_addr.select_one("span.addr").get_text()
            shop["cat"] = category
            shop["region"] = region
            shop["addr"] = addr
        except:
            pass

        try:
            rec_dish = txt.select("div.recommend > a")
            assert len(rec_dish) > 0
            rec_dish = [dish.get_text() for dish in rec_dish]
            shop["rec_dish"] = rec_dish
        except:
            pass

        try:
            comment_list = txt.select("span.comment-list > span > b")
            score_list = [float(sc.get_text()) for sc in comment_list]
            shop["score"] = {
                "taste": score_list[0],
                "env": score_list[1],
                "service": score_list[2],
            }
        except:
            pass

        shop_list.append(shop)
    return shop_list


def search_shops(city_id, keyword, page, get_proxies_fun=None):
    '''
    seach shops by keyword
    :param city_id: the id of the target city
    :param keyword: the keyword
    :param page: page index [1, 50]
    :return: a list of shops : [{"name": "shopname1", "shop_id": "1245587}, ...]
    '''
    url = "http://www.dianping.com/search/keyword/{}/0_{}/p{}".format(city_id, keyword, page)
    headers = requests_dora.get_default_headers()
    headers["Accept"] = 'application/json, text/javascript'
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    headers["Host"] = "www.dianping.com"
    del headers["Referer"]

    while True:
        res = requests_dora.try_best_2_get(url, get_proxies_fun=get_proxies_fun, headers=headers)
        if res.status_code == 200:
            break
        random.seed(time.time())
        sleep_time = 3 + 7 * random.random()
        logging.warning("failde ... try again in {} s...".format(sleep_time))
        time.sleep(sleep_time)

    html = res.text
    soup = BeautifulSoup(html, "lxml")
    li_list = soup.select("div.shop-list > ul > li")

    shop_list = []
    for li in li_list:
        shop = {}
        try:
            txt = li.select_one("div.txt")
            a_title = txt.select_one("div.tit > a")
            title = a_title["title"]
            shop_id = a_title["data-shopid"]
            shop["name"] = title
            shop["shop_id"] = shop_id
        except:
            continue
        shop_list.append(shop)

    return shop_list


def get_map_code2char(url):
    '''
    get the map for decrypting
    :param url: the url of the css file which is used for encrypt
    :return:
    '''
    headers = requests_dora.get_default_headers()
    headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    res = requests_dora.try_best_2_get(url, headers=headers)
    css = res.text
    it = re.finditer('span\[class\^="(.*?)"\]{.*?background-image:.*?url\((.*?)\)', css)

    map_key2char_global = {}
    for match in it:
        # extract the css selector
        css_sel_head = match.group(1)

        # extract the text
        svg_url = "https:{}".format(match.group(2))
        svg = requests_dora.try_best_2_get(svg_url, headers=headers)
        soup = BeautifulSoup(svg.text, "lxml")
        text_list = soup.select("text")
        text_list = [txt.text for txt in text_list]
        text = "".join(text_list)
        text = re.sub("\n", "", text)

        # map selectors to character
        pattern = "\.(%s.*?){background:(.*?)px (.*?)px;}" % css_sel_head
        it = re.finditer(pattern, css)
        map_char2pos = {}
        for match in it:
            key = match.group(1)
            y = match.group(2)
            x = match.group(3)
            map_char2pos[key] = (float(x), float(y))

        key_list = list(sorted(map_char2pos.keys(), key=lambda k: map_char2pos[k], reverse=True))
        tpl = zip(key_list, text)
        map_key2char = dict((i, j) for i, j in tpl)
        map_key2char_global = {**map_key2char_global, **map_key2char}
    return map_key2char_global


if __name__ == "__main__":
    # shop_list = search_shops("2", "4s店", 1)
    # print(shop_list)

    import json
    shop_list = get_around("2", "5724615", 2000, 2)
    print(json.dumps(shop_list, indent=2, ensure_ascii=False))

    # get the map to decrypt
    # url = "https://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/8d42683a9b290707dcf319a5920cff72.css"
    # map1 = get_map_code2char(url)
    # print(map1)
    pass
