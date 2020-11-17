
# Doraemon
**Doraemon is a tool kit.**

***
1. Google Knowledge Graph [Deprecated]
2. Google Translator
3. Dianping [Deprecated] # 大众点评 
4. QQ music lyrics
5. whois
6. NetEase music comments
7. Parse domain name to IP (in batch)
***

## Tools
### 1. Robust Requests
```python
from Doraemon import requests_dora
url = "https://www.baidu.com"

headers = requests_dora.get_default_headers()
headers["User-Agent"] = requests_dora.get_random_user_agent()

def get_proxies():
    proxy_str = "127.0.0.1:1080"
    proxies = {"http": "http://%s" % proxy_str,
               "https": "http://%s" % proxy_str, }
    return proxies

# max_times, get_proxies_fun, and invoked_by are optional parameters, others are the same as the requests.get() and requests.post()
res1 = requests_dora.try_best_2_get(url, max_times=5, get_proxies_fun=get_proxies, invoked_by="parent_fun_name") 
res2 = requests_dora.try_best_2_post(url, max_times=5, get_proxies_fun=get_proxies)
print(res1.status_code)
print(res2.status_code)
```
### 2. Proxy Kit
```python
from Doraemon import proxies_dora
proxies1 = proxies_dora.get_proxies("127.0.0.1:223") # get a self-defined proxies dict
proxies2 = proxies_dora.get_data5u_proxies("your data5u api key") # input api key for crawling, get a proxies dict

pool = [
"127.0.0.1:233",
"123.123.123.123:123",
"...",
]

proxies_dora.set_pool(pool) # set a self-defined proxy pool
proxies3 = proxies_dora.get_proxies_fr_pool() # get a proxies dict from the pool

loc_info1 = proxies_dora.loc_proxy_ipv4(proxies1) # get location info of a given proxy, ipv4 only
loc_info2 = proxies_dora.loc_proxy(proxies2) # get location info of a given proxy, for both ipv4 and ipv6

```
### 3. User-friendly Chrome
```python
from Doraemon import chrome_dora

proxy = "127.0.0.1:1080"
baidu_url = "https://www.baidu.com"
# no_images: do not load images(response more quickly)
# headless: make the chrome invisible
# proxy: set if you need
# they are all optional
chrome = chrome_dora.MyChrome(headless=False, proxy="127.0.0.1:1080", no_images=True) 
chrome.get(baidu_url)
print(chrome.page_source)
```

## Crawlers
### 1. Google Knowledge Graph [Deprecated]
```python
from Doraemon import google_KG

def get_proxies():
    proxy_str = "127.0.0.1:1080"
    proxies = {"http": "http://%s" % proxy_str,
               "https": "http://%s" % proxy_str, }
    return proxies

res = google_KG.get_entity("alibaba", get_proxies_fun=get_proxies)
print(res)
```

### 2. Google Translator
```python
from Doraemon import google_translator, proxies_dora

def get_proxies():
    proxy_str = "127.0.0.1:1080"
    proxies = {"http": "http://%s" % proxy_str,
               "https": "http://%s" % proxy_str, }
    return proxies

ori_text = "中华民国"
# sl, tl and get_proxies_fun are optional, the default values are "auto", "en", None
res1 = google_translator.trans(ori_text,sl="auto", tl="zh-TW", get_proxies_fun=get_proxies) 
# replace the function get_proxies with proxies_dora.get_proxies("127.0.0.1:1080")
res2 = google_translator.trans(ori_text,sl="auto", tl="zh-TW", get_proxies_fun=lambda: proxies_dora.get_proxies("127.0.0.1:1080")) 

long_text = ori_text * 2500 # 10000 characters
res3 = google_translator.trans_long(long_text)# if len(text) > 5000

print(res1)
print(res2)
```

**Language Code:**
```angular2html
检测语言: auto
阿尔巴尼亚语: sq
阿拉伯语: ar
阿姆哈拉语: am
阿塞拜疆语: az
爱尔兰语: ga
爱沙尼亚语: et
巴斯克语: eu
白俄罗斯语: be
保加利亚语: bg
冰岛语: is
波兰语: pl
波斯尼亚语: bs
波斯语: fa
布尔语(南非荷兰语): af
丹麦语: da
德语: de
俄语: ru
法语: fr
菲律宾语: tl
芬兰语: fi
弗里西语: fy
高棉语: km
格鲁吉亚语: ka
古吉拉特语: gu
哈萨克语: kk
海地克里奥尔语: ht
韩语: ko
豪萨语: ha
荷兰语: nl
吉尔吉斯语: ky
加利西亚语: gl
加泰罗尼亚语: ca
捷克语: cs
卡纳达语: kn
科西嘉语: co
克罗地亚语: hr
库尔德语: ku
拉丁语: la
拉脱维亚语: lv
老挝语: lo
立陶宛语: lt
卢森堡语: lb
罗马尼亚语: ro
马尔加什语: mg
马耳他语: mt
马拉地语: mr
马拉雅拉姆语: ml
马来语: ms
马其顿语: mk
毛利语: mi
蒙古语: mn
孟加拉语: bn
缅甸语: my
苗语: hmn
南非科萨语: xh
南非祖鲁语: zu
尼泊尔语: ne
挪威语: no
旁遮普语: pa
葡萄牙语: pt
普什图语: ps
齐切瓦语: ny
日语: ja
瑞典语: sv
萨摩亚语: sm
塞尔维亚语: sr
塞索托语: st
僧伽罗语: si
世界语: eo
斯洛伐克语: sk
斯洛文尼亚语: sl
斯瓦希里语: sw
苏格兰盖尔语: gd
宿务语: ceb
索马里语: so
塔吉克语: tg
泰卢固语: te
泰米尔语: ta
泰语: th
土耳其语: tr
威尔士语: cy
乌尔都语: ur
乌克兰语: uk
乌兹别克语: uz
西班牙语: es
希伯来语: iw
希腊语: el
夏威夷语: haw
信德语: sd
匈牙利语: hu
修纳语: sn
亚美尼亚语: hy
伊博语: ig
意大利语: it
意第绪语: yi
印地语: hi
印尼巽他语: su
印尼语: id
印尼爪哇语: jw
英语: en
约鲁巴语: yo
越南语: vi
中文(繁体): zh-TW
中文(简体): zh-CN
```
### 3. Dianping [Deprecated: character decoding]
```python
from Doraemon import dianping, proxies_dora
import json

# get_proxies_fun is optional, set if you want to use a proxy
shop_list = dianping.search_shops("2", "4s店", 1, get_proxies_fun=lambda: proxies_dora.get_proxies("127.0.0.1:1080")) # args: city id, keyword, page index
print(json.dumps(shop_list, indent=2, ensure_ascii=False))
# [{"name": "shopname1", "shop_id": "1245587}, ...]

# get_proxies_fun is optional, set if you want to use a proxy, this example use data5u proxy, 
# the website is :http://www.data5u.com/api/doc-dynamic.html 
shop_list_around = dianping.get_around("2", "5724615", 2000, 1, get_proxies_fun=lambda: proxies_dora.get_data5u_proxies("your data5u api key")) # args: city id, shop id, max distance, page index
print(json.dumps(shop_list_around, indent=2, ensure_ascii=False))
'''
shop_list_around is like this:
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
```

### 4. QQ music lyrics
```python
import os
from Doraemon import qq_music_crawler_by_album as qm_album, qq_music_crawler_by_area as qm_area
# crawl lyrics of songs in specific areas
area_list = ["港台", "内地"] # {'全部': -100, '内地': 200, '港台': 2, '欧美': 5, '日本': 4, '韩国': 3, '其他': 6}
save_path = "./qq_music_songs_by_area"
if not os.path.exists(save_path):
    os.makedirs(save_path)
qm_area.crawl_songs(area_list, save_path)

# crawl lyrics by albums
import json
from tqdm import tqdm

save_path = "./qq_music_songs_by_album"
if not os.path.exists(save_path):
    os.makedirs(save_path)

for sin in range(0, 7050, 30):
    ein = sin + 29
    album_list = qm_album.get_album_list(sin, ein) # get 30 albums

    for album in album_list:
        dissname = album["dissname"]
        song_list = qm_album.get_song_list(album["dissid"])
        chunk = []
        for song in tqdm(song_list, desc = "getting songs in {}".format(dissname)):
            contributors, lyric = qm_album.get_lyric(song)
            song["lyric"] = lyric
            chunk.append(song)

        json.dump(chunk, open("{}/lyric_{}.json".format(save_path, dissname), "w", encoding = "utf-8"), ensure_ascii = False)
```

### 5. whois
```python
from Doraemon import whois
ip_list = ["154.17.24.36", "154.17.24.37", "154.17.24.39", "154.17.21.36"] * 100
# # friendly
# res = whois.extract_org_names_friendly(ip_list, block_size = 100, sleep = 2)

# no limited
res = whois.extract_org_names_no_limited(ip_list)
print(res)
```

### 6. NetEase music comments 
run under `netease_music`
```bash
scrapy crawl comments
```

### 7. domain2ip
```python
from Doraemon import domain2ip
threads = 100
max_fail_num = 0
domain_name2ip = {} # results
url_list = ["https://www.baidu.com", "https://www.qq.com"]
domain2ip.gethostbyname_fast(url_list, domain_name2ip, threads, max_fail_num)
```
