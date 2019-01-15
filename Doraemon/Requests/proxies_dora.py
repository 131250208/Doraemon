import re
import logging
from Doraemon.Requests import requests_dora, settings
import time
import requests
from bs4 import BeautifulSoup
from Doraemon.Requests import proxies_dora

def get_data5u_proxies(api=None):
    url = "http://api.ip.data5u.com/dynamic/get.html?order=53b3de376027aa3f699dc335d2bc0674&sep=3"
    if api is not None:
        url = api

    res = requests_dora.try_best_2_get(url)
    proxy = res.text.strip()

    if not re.match("\d+\.\d+\.\d+\.\d+:\d+", proxy):
        logging.warning("the proxy expired...")
        raise Exception

    return get_proxies(proxy)


def get_proxies(proxy):
    proxies = {
        "http": "http://{}".format(proxy),
        "https": "https://{}".format(proxy),
    }
    logging.info("current proxy: {}".format(proxy))
    return proxies


def set_pool(pool):
    '''
    should be invoked before get_proxies_fr_pool
    :param pool:
    :return:
    '''
    settings.POOL = pool


def get_proxies_fr_pool():
    if len(settings.POOL) == 0:
        logging.warning("the POOL is dry...")
        raise Exception
    pool = settings.POOL
    len_pool = len(pool)
    index = int(time.time() % len_pool)
    proxy = pool[index]
    return get_proxies(proxy)


def loc_proxy_ipv4(proxies):
    test_res = requests_dora.try_best_2_get("http://lumtest.com/myip.json", max_times=2, proxies=proxies, timeout=10)
    if test_res is not None and test_res.status_code == 200:
        return(test_res.text)
    else:
        logging.warning("failed to connect to geolocation url ...")
        return None


def loc_proxy(proxies):
    res = requests_dora.try_best_2_get("https://proxy6.net/en/myip", max_times=2, proxies=proxies, timeout=10)
    soup = BeautifulSoup(res.text, "lxml")
    # ip = soup.select_one("div.block-head > h1").get_text()
    loc_div = soup.select_one("div.myip-row > div")
    line_list = loc_div.select("dl")
    loc_info = {}
    for line in line_list:
        key = line.select_one("dt").get_text().strip().lower()
        val = line.select_one("dd").get_text().strip()
        loc_info[key] = val

    return loc_info


if __name__ == "__main__":
    proxies = get_proxies("mwFoRq:bKkLJT@91.188.243.238:9299")
    print(loc_proxy(proxies))
    pass
