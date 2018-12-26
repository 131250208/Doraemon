import re
import logging
from Doraemon.Requests import requests_dora
import time
import requests
from bs4 import BeautifulSoup

def get_data5u_proxies(api=None):
    url = "http://api.ip.data5u.com/dynamic/get.html?order=53b3de376027aa3f699dc335d2bc0674&sep=3"
    if api is not None:
        url = api

    res = requests_dora.try_best_2_get(url)
    proxy = res.text.strip()

    if not re.match("\d+\.\d+\.\d+\.\d+:\d+", proxy):
        logging.warning("the proxy expired...")
        raise Exception

    proxies = {
        "http": "http://{}".format(proxy),
        "https": "https://{}".format(proxy),
    }
    logging.warning("current proxy: {}".format(proxy))
    return proxies


def get_proxies(proxy):
    proxies = {
        "http": "http://{}".format(proxy),
        "https": "https://{}".format(proxy),
    }
    logging.warning("current proxy: {}".format(proxy))
    return proxies


def get_proxies_fr_pool(pool):
    len_pool = len(pool)
    index = int(time.time() % len_pool)
    proxy = pool[index]
    return get_proxies(proxy)


def loc_proxies_ipv4(proxies):
    test_res = requests_dora.try_best_2_get("http://lumtest.com/myip.json", max_times=2, proxies=proxies, timeout=10)
    if test_res is not None and test_res.status_code == 200:
        logging.warning(test_res.text)
    else:
        logging.warning("failed to connect to geolocation url ...")


def detail_proxies(proxies):
    test_res = requests_dora.try_best_2_get("http://ipv6.baidu.com/s?wd=ip", max_times=2, proxies=proxies, timeout=20)
    if test_res is not None and test_res.status_code == 200:
        soup = BeautifulSoup(test_res.text, "lxml")
        ip_detail = soup.select_one("div.op-ip-detail")
        if ip_detail is not None:
            logging.warning(ip_detail.get_text())
    else:
        logging.warning("failed to connect to geolocation url ...")
    ""

if __name__ == "__main__":
    pool = [
        "168.235.109.152:15028",
        "168.235.109.152:15027",
        "168.235.109.152:15026",
        "168.235.109.152:15025",
        "168.235.109.152:15024",
        "168.235.109.152:15023",
        "168.235.109.152:15022",
        "168.235.109.152:15021",
        "168.235.109.152:15020",
        "168.235.109.152:15019",
        "91.208.149.215:8000",
    ]
    while True:
        proxies = get_proxies_fr_pool(pool)
        detail_proxies(proxies)
        time.sleep(1)
