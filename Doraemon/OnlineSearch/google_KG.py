import random
import time
from bs4 import BeautifulSoup
from urllib import parse
import re
from Doraemon.Requests import requests_dora, proxies_dora
import pyprind
import logging


ORG_KEYWORDS = ["college", "company", "university", "school", "corporation",
                    "institute", "organization", "association"]


def quote(queryStr):
    try:
        queryStr = parse.quote(queryStr)
    except:
        queryStr = parse.quote(queryStr.encode('utf-8', 'ignore'))

    return queryStr


def google_search(queryStr, get_proxies_fun):
    queryStr = quote(queryStr)
    url = 'https://www.google.com/search?biw=1920&safe=active&hl=en&q=%s&oq=%s' % (queryStr, queryStr)

    response = requests_dora.try_best_2_get(url, headers=requests_dora.get_default_headers(), invoked_by="google_search", get_proxies_fun=get_proxies_fun)
    html = ""
    status = response.status_code
    if status == 200:
        html = response.text
    else:
        print("status: {}, try again....".format(status))
        random.seed(time.time())
        time.sleep(3 + 5 * random.random())
        return google_search(queryStr, get_proxies_fun)
    return html


def get_entity(query_str, get_proxies_fun, wait=1.5):
    '''
    get more relevant org name by search engine(google
    :param query_set:
    :param tag:
    :return: relevant organization name list
    '''

    rel_org_name_set = set()
    logging.warning("start crawling {}...".format(query_str))

    text = google_search(query_str, get_proxies_fun)
    random.seed(time.time())
    time.sleep(wait * random.random())

    soup = BeautifulSoup(text, "lxml")

    # it there an entity in google KG?
    div_kg_hearer = soup.select_one("div.kp-header")

    if div_kg_hearer is None: # if there is no knowledge graph at the right, drop it
        logging.warning("no entity returned for this query")
        return None

    enti_name = div_kg_hearer.select_one("div[role=heading] span")
    enti_name = enti_name.text if enti_name is not None else None
    if enti_name is None or "..." in enti_name:
        se = re.search('\["t-dhmk9MkDbvI",.*\[\["data",null,null,null,null,\[null,"\[\\\\"(.*)\\\\",', text)
        if se is not None:
            enti_name = se.group(1)
        else:
            logging.warning("sth went wrong when extracting the name of the entity")
            return None

    # identify the type
    span_list = div_kg_hearer.select("span")
    enti_type = span_list[-1].text if len(span_list) > 1 else "unknown"

    # description from wikipedia
    des = soup.find("h3", text="Description")
    des_info = ""
    if des is not None:
        des_span = des.parent.select_one("span")
        des_info = des_span.text if des_span is not None else ""

    # identify whether it is a organization
    pattern_org = "(%s)" % "|".join(ORG_KEYWORDS)
    se = re.search(pattern_org, enti_type, flags=re.I)
    is_org = False if se is None else True

    # extract attributes
    attr_tags = soup.select("div.Z1hOCe")
    attr_dict = {}
    for attr in attr_tags:
        attr_str = attr.get_text()
        se = re.search("(.*?)[:：](.*)", attr_str)
        if se is None:
            continue
        key_attr = se.group(1)
        val_attr = se.group(2)
        attr_dict[key_attr] = val_attr

    # relevant org name on current page
    a_reltype_list = soup.select("div.MRfBrb > a")
    for a in a_reltype_list:
        rel_org_name_set.add(a["title"].strip())

    # collect next urls e.g. : more x+
    div_list = soup.select("div.yp1CPe")
    next = []
    host = "https://www.google.com"
    for div in div_list:
        a_list = div.select("a.EbH0bb")
        for a in a_list:
            if "http" not in a["href"]:
                next.append("%s%s" % (host, a["href"]))

    # crawl parent org
    a_parent_org = soup.find("a", text="Parent organization")
    if a_parent_org is not None:
        parent_str = a_parent_org.parent.parent.text.strip()
        parent_org = parent_str.split(":")[1]
        rel_org_name_set.add(parent_org.strip())

    # crawl subsidiaries
    a_subsidiaries = soup.find("a", text="Subsidiaries")
    if a_subsidiaries is not None:
        href = a_subsidiaries["href"]
        if "http" not in href:
            subsidiaries_str = a_subsidiaries.parent.parent.text.strip()
            subs = subsidiaries_str.split(":")[1].split(",")
            for sub in subs:
                sub = sub.strip()
                if sub == "MORE":
                    continue
                rel_org_name_set.add(sub)
            next.append("%s%s" % (host, href))

    # scrawl urls in list 'next'
    bar = pyprind.ProgBar(len(next), title="crawling relevant org names...")
    for url in next:
        res = requests_dora.try_best_2_get(url, invoked_by="get_org_name", headers=requests_dora.get_default_headers(), get_proxies_fun=get_proxies_fun)
        soup = BeautifulSoup(res.text, "lxml")

        # crawl items at the top
        a_list = soup.select("a.klitem")
        for a in a_list:
            rel_org_name = a["title"]
            rel_org_name_set.add(rel_org_name.strip())

        # crawl headings under the map if any
        heading_list = soup.select("div.VkpGBb")
        for heading in heading_list:
            heading_str = heading.select_one("div[role='heading']")
            rel_org_name_set.add(heading_str.get_text())

        random.seed(time.time())
        bar.update()
        time.sleep(wait * random.random())

    rel_org_name_list = [org_name for org_name in rel_org_name_set if len(org_name) > 1]
    return {"query_str": query_str, "name": enti_name, "type": enti_type, "is_org": is_org,
            "des": des_info, "attributes": attr_dict, "rel_org": rel_org_name_list}


if __name__ == "__main__":
    def get_proxies():
        proxies = {
        "http": "http://127.0.0.1:1080",
        "https": "https://127.0.0.1:1080",
        }
        return proxies

    # Association of Public and Land‑grant ...
    res = get_entity("Roubaix", get_proxies_fun=get_proxies)
    print(res)


