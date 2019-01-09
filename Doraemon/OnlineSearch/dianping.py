from Doraemon import requests_dora, proxies_dora
from bs4 import BeautifulSoup
import re


def get_around(city, shop_id_center, dis, page):
    url = "http://www.dianping.com/search/around/{}/10_{}/d{}p{}".format(city, shop_id_center, dis, page)
    headers = requests_dora.get_default_headers()
    headers["Accept"] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    headers["User-Agent"] = requests_dora.get_random_user_agent()
    headers["Host"] = "www.dianping.com"
    headers["Referer"] = "http://www.dianping.com/search/around/2/10_5724615/d2000"

    while True:
        res = requests_dora.try_best_2_get(url, get_proxies_fun=proxies_dora.get_data5u_proxies, headers=headers)
        if res.status_code == 200:
            break
    html = res.text
    url = "https:{}".format(re.search('href="(//s3plus\.meituan\.net.*?\.css)">', html).group(1))
    map_code2char = get_map_code2char(url)
    it = re.finditer('<span class="([0-9a-zA-Z]*?)"></span>', html)
    for match in it:
        code = match.group(1)
        if code in map_code2char:
            html = re.sub('<span class="{}"></span>'.format(code), map_code2char[code], html)

    soup = BeautifulSoup(html, "lxml")
    li_list = soup.select("div.shop-list > ul > li")

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
            pass

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

def search(keyword, page):
    url = "http://www.dianping.com/search/keyword/2/0_{}/p{}".format(keyword, page)


def get_map_code2char(url):
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
    shop_list = get_around("2", "5724615", 2000, 2)
    print(shop_list)
    # url = "https://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/8d42683a9b290707dcf319a5920cff72.css"
    # map1 = get_map_code2char(url)
    # print(map1)
    pass
