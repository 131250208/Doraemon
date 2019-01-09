from Doraemon import requests_dora
from bs4 import BeautifulSoup


def get_around(city, shop_id_center, dis, page):
    url = "http://www.dianping.com/search/around/{}/10_{}/d{}p{}".format(city, shop_id_center, dis, page)
    headers = requests_dora.get_default_headers()
    headers["Accept"] = 'application/json, text/javascript'
    headers["Host"] = "www.dianping.com"
    del headers["Referer"]
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    res = requests_dora.try_best_2_get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")


def search(keyword, page):
    url = "http://www.dianping.com/search/keyword/2/0_{}/p{}".format(keyword, page)


if __name__ == "__main__":
    get_around("9", "112506898", 2000, 1)

    # text=get_chinese()#text是所有文字集合
    # changedic=number()#changedic是数字对应的字典
    # #这里的url是随意找的五个类
    # urls = ['http://www.dianping.com/shop/77335766', 'http://www.dianping.com/shop/9799086','http://www.dianping.com/shop/92871773',
    #          'http://www.dianping.com/shop/23635007','http://www.dianping.com/shop/78965850']
    # result=chinese(text)#result是汉字对应的字典
    # #print(result)
    # comment(result,urls)#获得评论数据
    # score(changedic, urls)#获得评分等数据