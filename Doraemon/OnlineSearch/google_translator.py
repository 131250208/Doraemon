# -*- coding:utf-8 -*-
import requests
import re
import execjs
import json
import logging
import html
import time
import pyprind
from Doraemon.Requests import requests_dora

'''reference: language 2 code

{code:'auto',name:'检测语言'},{code:'sq',name:'阿尔巴尼亚语'},{code:'ar',name:'阿拉伯语'},{code:'am',name:'阿姆哈拉语'},{code:'az',name:'阿塞拜疆语'},{code:'ga',name:'爱尔兰语'},{code:'et',name:'爱沙尼亚语'},{code:'eu',name:'巴斯克语'},{code:'be',name:'白俄罗斯语'},{code:'bg',name:'保加利亚语'},{code:'is',name:'冰岛语'},{code:'pl',name:'波兰语'},{code:'bs',name:'波斯尼亚语'},{code:'fa',name:'波斯语'},{code:'af',name:'布尔语(南非荷兰语)'},{code:'da',name:'丹麦语'},{code:'de',name:'德语'},{code:'ru',name:'俄语'},{code:'fr',name:'法语'},{code:'tl',name:'菲律宾语'},{code:'fi',name:'芬兰语'},{code:'fy',name:'弗里西语'},{code:'km',name:'高棉语'},{code:'ka',name:'格鲁吉亚语'},{code:'gu',name:'古吉拉特语'},{code:'kk',name:'哈萨克语'},{code:'ht',name:'海地克里奥尔语'},{code:'ko',name:'韩语'},{code:'ha',name:'豪萨语'},{code:'nl',name:'荷兰语'},{code:'ky',name:'吉尔吉斯语'},{code:'gl',name:'加利西亚语'},{code:'ca',name:'加泰罗尼亚语'},{code:'cs',name:'捷克语'},{code:'kn',name:'卡纳达语'},{code:'co',name:'科西嘉语'},{code:'hr',name:'克罗地亚语'},{code:'ku',name:'库尔德语'},{code:'la',name:'拉丁语'},{code:'lv',name:'拉脱维亚语'},{code:'lo',name:'老挝语'},{code:'lt',name:'立陶宛语'},{code:'lb',name:'卢森堡语'},{code:'ro',name:'罗马尼亚语'},{code:'mg',name:'马尔加什语'},{code:'mt',name:'马耳他语'},{code:'mr',name:'马拉地语'},{code:'ml',name:'马拉雅拉姆语'},{code:'ms',name:'马来语'},{code:'mk',name:'马其顿语'},{code:'mi',name:'毛利语'},{code:'mn',name:'蒙古语'},{code:'bn',name:'孟加拉语'},{code:'my',name:'缅甸语'},{code:'hmn',name:'苗语'},{code:'xh',name:'南非科萨语'},{code:'zu',name:'南非祖鲁语'},{code:'ne',name:'尼泊尔语'},{code:'no',name:'挪威语'},{code:'pa',name:'旁遮普语'},{code:'pt',name:'葡萄牙语'},{code:'ps',name:'普什图语'},{code:'ny',name:'齐切瓦语'},{code:'ja',name:'日语'},{code:'sv',name:'瑞典语'},{code:'sm',name:'萨摩亚语'},{code:'sr',name:'塞尔维亚语'},{code:'st',name:'塞索托语'},{code:'si',name:'僧伽罗语'},{code:'eo',name:'世界语'},{code:'sk',name:'斯洛伐克语'},{code:'sl',name:'斯洛文尼亚语'},{code:'sw',name:'斯瓦希里语'},{code:'gd',name:'苏格兰盖尔语'},{code:'ceb',name:'宿务语'},{code:'so',name:'索马里语'},{code:'tg',name:'塔吉克语'},{code:'te',name:'泰卢固语'},{code:'ta',name:'泰米尔语'},{code:'th',name:'泰语'},{code:'tr',name:'土耳其语'},{code:'cy',name:'威尔士语'},{code:'ur',name:'乌尔都语'},{code:'uk',name:'乌克兰语'},{code:'uz',name:'乌兹别克语'},{code:'es',name:'西班牙语'},{code:'iw',name:'希伯来语'},{code:'el',name:'希腊语'},{code:'haw',name:'夏威夷语'},{code:'sd',name:'信德语'},{code:'hu',name:'匈牙利语'},{code:'sn',name:'修纳语'},{code:'hy',name:'亚美尼亚语'},{code:'ig',name:'伊博语'},{code:'it',name:'意大利语'},{code:'yi',name:'意第绪语'},{code:'hi',name:'印地语'},{code:'su',name:'印尼巽他语'},{code:'id',name:'印尼语'},{code:'jw',name:'印尼爪哇语'},{code:'en',name:'英语'},{code:'yo',name:'约鲁巴语'},{code:'vi',name:'越南语'},{code:'zh-CN',name:'中文'}],target_code_name:[{code:'sq',name:'阿尔巴尼亚语'},{code:'ar',name:'阿拉伯语'},{code:'am',name:'阿姆哈拉语'},{code:'az',name:'阿塞拜疆语'},{code:'ga',name:'爱尔兰语'},{code:'et',name:'爱沙尼亚语'},{code:'eu',name:'巴斯克语'},{code:'be',name:'白俄罗斯语'},{code:'bg',name:'保加利亚语'},{code:'is',name:'冰岛语'},{code:'pl',name:'波兰语'},{code:'bs',name:'波斯尼亚语'},{code:'fa',name:'波斯语'},{code:'af',name:'布尔语(南非荷兰语)'},{code:'da',name:'丹麦语'},{code:'de',name:'德语'},{code:'ru',name:'俄语'},{code:'fr',name:'法语'},{code:'tl',name:'菲律宾语'},{code:'fi',name:'芬兰语'},{code:'fy',name:'弗里西语'},{code:'km',name:'高棉语'},{code:'ka',name:'格鲁吉亚语'},{code:'gu',name:'古吉拉特语'},{code:'kk',name:'哈萨克语'},{code:'ht',name:'海地克里奥尔语'},{code:'ko',name:'韩语'},{code:'ha',name:'豪萨语'},{code:'nl',name:'荷兰语'},{code:'ky',name:'吉尔吉斯语'},{code:'gl',name:'加利西亚语'},{code:'ca',name:'加泰罗尼亚语'},{code:'cs',name:'捷克语'},{code:'kn',name:'卡纳达语'},{code:'co',name:'科西嘉语'},{code:'hr',name:'克罗地亚语'},{code:'ku',name:'库尔德语'},{code:'la',name:'拉丁语'},{code:'lv',name:'拉脱维亚语'},{code:'lo',name:'老挝语'},{code:'lt',name:'立陶宛语'},{code:'lb',name:'卢森堡语'},{code:'ro',name:'罗马尼亚语'},{code:'mg',name:'马尔加什语'},{code:'mt',name:'马耳他语'},{code:'mr',name:'马拉地语'},{code:'ml',name:'马拉雅拉姆语'},{code:'ms',name:'马来语'},{code:'mk',name:'马其顿语'},{code:'mi',name:'毛利语'},{code:'mn',name:'蒙古语'},{code:'bn',name:'孟加拉语'},{code:'my',name:'缅甸语'},{code:'hmn',name:'苗语'},{code:'xh',name:'南非科萨语'},{code:'zu',name:'南非祖鲁语'},{code:'ne',name:'尼泊尔语'},{code:'no',name:'挪威语'},{code:'pa',name:'旁遮普语'},{code:'pt',name:'葡萄牙语'},{code:'ps',name:'普什图语'},{code:'ny',name:'齐切瓦语'},{code:'ja',name:'日语'},{code:'sv',name:'瑞典语'},{code:'sm',name:'萨摩亚语'},{code:'sr',name:'塞尔维亚语'},{code:'st',name:'塞索托语'},{code:'si',name:'僧伽罗语'},{code:'eo',name:'世界语'},{code:'sk',name:'斯洛伐克语'},{code:'sl',name:'斯洛文尼亚语'},{code:'sw',name:'斯瓦希里语'},{code:'gd',name:'苏格兰盖尔语'},{code:'ceb',name:'宿务语'},{code:'so',name:'索马里语'},{code:'tg',name:'塔吉克语'},{code:'te',name:'泰卢固语'},{code:'ta',name:'泰米尔语'},{code:'th',name:'泰语'},{code:'tr',name:'土耳其语'},{code:'cy',name:'威尔士语'},{code:'ur',name:'乌尔都语'},{code:'uk',name:'乌克兰语'},{code:'uz',name:'乌兹别克语'},{code:'es',name:'西班牙语'},{code:'iw',name:'希伯来语'},{code:'el',name:'希腊语'},{code:'haw',name:'夏威夷语'},{code:'sd',name:'信德语'},{code:'hu',name:'匈牙利语'},{code:'sn',name:'修纳语'},{code:'hy',name:'亚美尼亚语'},{code:'ig',name:'伊博语'},{code:'it',name:'意大利语'},{code:'yi',name:'意第绪语'},{code:'hi',name:'印地语'},{code:'su',name:'印尼巽他语'},{code:'id',name:'印尼语'},{code:'jw',name:'印尼爪哇语'},{code:'en',name:'英语'},{code:'yo',name:'约鲁巴语'},{code:'vi',name:'越南语'},{code:'zh-TW',name:'中文(繁体)'},{code:'zh-CN',name:'中文(简体)'}
'''


js = '''
    function b(a, b) {
        for (var d = 0; d < b.length - 2; d += 3) {
            var c = b.charAt(d + 2),
                c = "a" <= c ? c.charCodeAt(0) - 87 : Number(c),
                c = "+" == b.charAt(d + 1) ? a >>> c : a << c;
            a = "+" == b.charAt(d) ? a + c & 4294967295 : a ^ c
        }
        return a
    }

    function tk(a,TKK) {
        for (var e = TKK.split("."), h = Number(e[0]) || 0, g = [], d = 0, f = 0; f < a.length; f++) {
            var c = a.charCodeAt(f);
            128 > c ? g[d++] = c : (2048 > c ? g[d++] = c >> 6 | 192 : (55296 == (c & 64512) && f + 1 < a.length && 56320 == (a.charCodeAt(f + 1) & 64512) ? (c = 65536 + ((c & 1023) << 10) + (a.charCodeAt(++f) & 1023), g[d++] = c >> 18 | 240, g[d++] = c >> 12 & 63 | 128) : g[d++] = c >> 12 | 224, g[d++] = c >> 6 & 63 | 128), g[d++] = c & 63 | 128)
        }
        a = h;
        for (d = 0; d < g.length; d++) a += g[d], a = b(a, "+-a^+6");
        a = b(a, "+-3^+b+-f");
        a ^= Number(e[1]) || 0;
        0 > a && (a = (a & 2147483647) + 2147483648);
        a %= 1E6;
        return a.toString() + "." + (a ^ h)
    }
    '''
tk_calculator = execjs.compile(js)  # use to compute the token for translating request


def get_TKK(get_proxies_fun=None):
    '''
    to get a value for calculating the token for constructing translating request
    :return: TKK
    '''
    url = "https://translate.google.cn"
    logging.warning("start getting tkk...")

    res = requests_dora.try_best_2_get(url, get_proxies_fun=get_proxies_fun)

    TKK = re.search("tkk:'(.*?)'", res.text).group(1)
    return TKK


def trans_req(ori_text, sl="auto", tl="en", get_proxies_fun=None):
    '''
    construct translating request
    :param ori_text:
    :param sl:
    :param tl:
    :return:
    '''
    ori_text = html.unescape(ori_text)  # unescape the html
    res = None

    while True:
        try:
            tk = tk_calculator.call("tk", ori_text, get_TKK())

            url_trans = "https://translate.google.cn/translate_a/single"

            payload = {
                "client": "t",
                "sl": sl,
                "tl": tl,
                "dt": "t",
                "ie": "UTF-8",
                "oe": "UTF-8",
                "otf": "1",
                "ssel": "0",
                "tsel": "0",
                "kc": "1",
                "tk": tk,
                "q": ori_text,
            }

            # res = req_t_death("POST", url_trans, payload)
            res = requests_dora.try_best_2_post(url_trans, data=payload, get_proxies_fun=get_proxies_fun)
            # print(res.text)
        except Exception as e:
            logging.warning(e)
            logging.warning("error, waiting and try again...")
            # logging.warning("text: %s " % ori_text)
            time.sleep(1)
            continue

        if res.status_code == 200:
            break

    js = None
    try:
        js = json.loads(res.text)
    except Exception as e:
        logging.warning(e)
        return []

    return js


def get_language_type(ori_text, get_proxies_fun=None):
    '''
    identify which language it is
    :param ori_text:
    :return:
    '''
    info = ori_text[:30] if len(ori_text) > 30 else ori_text
    logging.warning("start identifying: {}...".format(info))
    js = trans_req(ori_text, get_proxies_fun)
    return js[2]


def trans(ori_text, sl="auto", tl="en", get_proxies_fun=None):
    '''
    translate text of which the length is less than 5000
    :param ori_text:
    :param sl:
    :param tl:
    :return:
    '''
    info = ori_text[:50] if len(ori_text) > 50 else ori_text
    logging.warning("start translating: {}...".format(info))

    js = trans_req(ori_text, sl, tl, get_proxies_fun)
    trans_text = ""
    if js[2] == "en":
        trans_text = js[0][0][0]
    else:
        for pas in js[0]:
            trans_text += pas[0]

    info = trans_text[:50] if len(trans_text) > 50 else trans_text
    logging.warning("translation result: {}...".format(info))
    return trans_text


def trans_long(ori_text, sl="auto", tl="en", get_proxies_fun=None):
    '''
    split the long text into pieces and translate

    :param ori_text: text whose len > 5000
    :param sl: source language
    :param tl: target language
    :return:
    '''
    stop_char = ["。", ".", ]
    start_flag = 0
    split_marks = []

    pointor = start_flag + 5000 + 1

    while True:
        while ori_text[pointor] not in stop_char:
            pointor -= 1
        split_marks.append(pointor)
        pointor += 5000
        if pointor >= len(ori_text):
            break

    snippets = []
    start_flag = 0
    for m in split_marks:
        snippets.append(ori_text[start_flag:(m + 1)])
        start_flag = m + 1

    if split_marks[-1] != len(ori_text) - 1:
        snippets.append(ori_text[start_flag:len(ori_text)])

    if get_language_type(snippets[0]) == tl:
        return ori_text

    en_text = ""
    for sni in pyprind.prog_bar(snippets):
        en_text += trans(sni, sl, tl, get_proxies_fun)

    return en_text


if __name__ == "__main__":
    def get_proxy():
        proxy_str = requests.get(
            "http://api.ip.data5u.com/dynamic/get.html?order=53b3de376027aa3f699dc335d2bc0674&sep=3").text.strip()
        proxies = {"http": "http://%s" % proxy_str,
                   "https": "http://%s" % proxy_str, }
        return proxies

    res = trans("中华民国", get_proxies_fun=get_proxy)
    print(res)
    pass
