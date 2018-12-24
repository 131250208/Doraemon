
Doraemon is a toolkit including frequently used code. It is still in development...
# Installation
```bash
pip install Doraemon
```

# Checklist
1. Google Knowledge Graph
2. Google Translator
3. Robust Requests
4. User-friendly Chrome

# Example
##1. Google Knowledge Graph
```python
from Doraemon.OnlineSearch import google_KG

def get_proxies():
    proxy_str = "127.0.0.1:1080"
    proxies = {"http": "http://%s" % proxy_str,
               "https": "http://%s" % proxy_str, }
    return proxies

res = google_KG.get_entity("alibaba", get_proxies_fun=get_proxies)
print(res)
```

##2. Google Translator
```python
from Doraemon.OnlineSearch import google_translator

def get_proxies():
    proxy_str = "127.0.0.1:1080"
    proxies = {"http": "http://%s" % proxy_str,
               "https": "http://%s" % proxy_str, }
    return proxies

ori_text = "中华民国"
# sl, tl and get_proxies_fun are optional, the default values are "auto", "en", None
res1 = google_translator.trans(ori_text,sl="auto", tl="zh-TW", get_proxies_fun=get_proxies)
long_text = ori_text * 2500 
res2 = google_translator.trans_long(long_text)# if len(text) > 5000

print(res1)
print(res2)

```
### Language Code:
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


##3. Robust Requests
```python
from Doraemon.Requests import requests_dora
url = "https://www.baidu.com"

headers = requests_dora.get_default_headers()
headers["User-Agent"] = requests_dora.get_random_user_agent()

def get_proxies():
    proxy_str = "127.0.0.1:1080"
    proxies = {"http": "http://%s" % proxy_str,
               "https": "http://%s" % proxy_str, }
    return proxies

# max_times, get_proxies_fun, and invoked_by is optional, other parameters are the same as the requests.get() and requests.post()
res1 = requests_dora.try_best_2_get(url, max_times=5, get_proxies_fun=get_proxies, invoked_by="parent_fun_name") 
res2 = requests_dora.try_best_2_post(url, max_times=5, get_proxies_fun=get_proxies)
print(res1.status_code)
print(res2.status_code)
```

##4. User-friendly Chrome
```python
from Doraemon.Requests import chrome_dora

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

