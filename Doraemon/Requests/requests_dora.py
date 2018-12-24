import logging
import random
import sys
import time
import requests
from Doraemon.Requests import settings
import re


def get_data5u_proxies(api=None):
    url = "http://api.ip.data5u.com/dynamic/get.html?order=53b3de376027aa3f699dc335d2bc0674&sep=3"
    if api is not None:
        url = api

    res = try_best_2_get(url)
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


def get_default_headers():
    headers = settings.HEADERS
    ip_byte1 = random.randint(121, 255)
    ip_byte2 = random.randint(121, 255)
    ip_byte3 = random.randint(121, 255)
    ip_byte4 = random.randint(121, 255)
    headers["Referer"] = "{}.{}.{}.{}".format(ip_byte1, ip_byte2, ip_byte3, ip_byte4)
    return headers


def get_random_user_agent():
    random.seed(time.time())
    return random.choice(settings.USER_AGENTS)


def try_best_2_post(url, data=None, json=None, max_times=999, invoked_by=None, proxies=None, get_proxies_fun=None, **kwargs):
    '''
    :param url:
    :param data:
    :param json:
    :param max_times: max times for trying
    :param invoked_by: invoked by which function, used to debug
    :param get_proxies_fun: invoke the get_proxies_fun every request if it's been set
    :param proxies: it does not work if the get_proxies_fun has been set
    :param kwargs:
    :return:
    '''
    error_count = 0
    if invoked_by is None:
        invoked_by = "not set"
    while True:
        try:
            if get_proxies_fun:
                proxies = get_proxies_fun()
            res = requests.post(url, data=data, json=json, proxies=proxies, **kwargs)
            break
        except Exception as e:
            logging.warning("%s(invoked by: %s) go wrong..., attempt: %d" % (
            sys._getframe().f_code.co_name, invoked_by, error_count))
            logging.warning(e)
            random.seed(time.time())
            time.sleep(2 + 3 * random.random())
            error_count += 1
            if error_count > max_times:
                logging.warning("max error_count exceeded: %d" % (max_times))
                return None
    return res


def try_best_2_get(url, params=None, max_times=999, invoked_by=None, proxies=None, get_proxies_fun=None, **kwargs):
    '''
    :param url:
    :param params:
    :param max_times: max times for trying
    :param invoked_by: invoked by which function, used to debug
    :param get_proxies_fun: invoke the get_proxies_fun every request if it's been set
    :param proxies: it does not work if the get_proxies_fun has been set
    :param kwargs:
    :return:
    '''
    error_count = 0
    if invoked_by is None:
        invoked_by = "not set"
    while True:
        try:
            if get_proxies_fun:
                proxies = get_proxies_fun()
            res = requests.get(url, params=params, proxies=proxies, **kwargs)
            break
        except Exception as e:
            logging.warning("%s(invoked by: %s) go wrong..., attempt: %d" % (sys._getframe().f_code.co_name, invoked_by, error_count))
            logging.warning(e)
            random.seed(time.time())
            time.sleep(2 + 3 * random.random())
            error_count += 1
            if error_count > max_times:
                logging.warning("max error_count exceeded: %d" % (max_times))
                return None
    return res


if __name__ == "__main__":
    google_url = "https://www.google.com"
    proxy = "127.0.0.1:1080"
    proxies = {
        "https": "https://{}".format(proxy),
        "http": "http://{}".format(proxy),
    }
    print(try_best_2_get(google_url, max_times=3, timeout=5, headers=get_default_headers(), proxies=proxies).status_code)