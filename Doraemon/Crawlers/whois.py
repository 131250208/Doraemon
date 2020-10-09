from Doraemon import requests_dora
import json
import re


def get_org_name_by_ripe(ip):
    api = "https://rest.db.ripe.net/search.json?source=ripe&query-string=%s" % ip # &source=apnic-grs
    res = requests_dora.try_best_2_get(api, timeout=30, invoked_by="get_org_name_by_ripe")
    if res is None or res.status_code != 200:
        return None

    try:
        json_res = json.loads(res.text)
        list_object = json_res["objects"]["object"]

        whois = {"ip": ip, "from": "RIPE NCC"}
        for ob in list_object:
            if ob["type"] == "organisation":
                list_attr = ob["attributes"]["attribute"]
                for attr in list_attr:
                    if attr["name"] == "org-name":
                        whois["org_name"] = attr["value"]
            elif ob["type"] == "inetnum":
                list_attr = ob["attributes"]["attribute"]
                for attr in list_attr:
                    if attr["name"] == "inetnum":
                        se = re.search("(.*?) - (.*)", attr["value"])
                        whois["start_address"] = se.group(1)
                        whois["end_address"] = se.group(2)
        assert "org_name" in whois and "start_address" in whois and "end_address" in whois
        return whois
    except Exception:
        return None


def get_org_name_by_arin(ip):
    api = "https://whois.arin.net/rest/ip/%s.json" % ip
    res = requests_dora.try_best_2_get(api, invoked_by="get_org_name_by_arin", timeout=30)
    if res is None or res.status_code != 200:
        return None

    handle_json = json.loads(res.text)
    handle = handle_json["net"]["handle"]["$"]
    # soup = BeautifulSoup(res.text, "lxml")
    # handle = soup.select_one("handle").text

    api2 = "https://whois.arin.net/rest/net/%s/pft.json?s=%s" % (handle, ip)
    res = requests_dora.try_best_2_get(api2, invoked_by="get_org_name_by_arin", timeout=30)
    if res is None or res.status_code != 200:
        return None

    name = None
    start_address = None
    end_address = None
    json_whois = json.loads(res.text)["ns4:pft"]

    if "org" in json_whois:
        org = json_whois["org"]
        name = org["name"]["$"]
    if "customer" in json_whois:
        customer = json_whois["customer"]
        name = customer["name"]["$"]

    if "net" in json_whois:
        start_address = json_whois["net"]["startAddress"]["$"]
        end_address = json_whois["net"]["endAddress"]["$"]

    return {
            "ip": ip,
            "start_address": start_address,
            "end_address": end_address,
            "org_name": name,
            "from": "ARIN",
        }


def get_org_name_by_lacnic(ip):
    api = "https://rdap.registro.br/ip/%s" % ip
    res = requests_dora.try_best_2_get(api, timeout=30, invoked_by="get_org_name_by_lacnic")
    if res is None or res.status_code != 200:
        return None

    json_whois = json.loads(res.text)

    list_vcard = json_whois["entities"][0]["vcardArray"][1]
    for c in list_vcard:
        if c[0] == "fn":
            whois = c[3]
            whois["ip"] = ip
            whois["from"] = "LACNIC"
            return whois

    return None


def get_org_name_by_apnic(ip):
    api = "http://wq.apnic.net/query?searchtext=%s" % ip
    res = requests_dora.try_best_2_get(api, invoked_by="get_org_name_by_apnic", timeout=30)
    if res is None or res.status_code != 200:
        return None

    json_whois = json.loads(res.text)
    try:
        for entry in json_whois:
            if entry["type"] == "object" and entry["objectType"] == "inetnum":
                attrs = entry["attributes"]
                for attr in attrs:
                    if attr["name"] == "descr":
                        whois = attr["values"][0]
                        whois["ip"] = ip
                        whois["from"] = "APNIC"
                        return whois
    except Exception:
        pass

    return None


def get_org_name_by_registration_db(ip):
    org = get_org_name_by_arin(ip)
    # Asia Pacific Network Information Centre, South Brisbane #

    if org is not None and "Asia Pacific Network Information Centre" in org["org_name"]:
        org = get_org_name_by_apnic(ip)

    elif org is not None and "RIPE Network Coordination Centre" in org["org_name"]:
        org = get_org_name_by_ripe(ip)

    elif org is not None and "Latin American and Caribbean IP address Regional Registry" in org["org_name"]:
        org = get_org_name_by_lacnic(ip)

    elif org is None:
        return None

    # org = ner_tool.filter_out_company_char(org)

    return org


if __name__ == "__main__":
    ip_list = list(json.load(open("./probes_ripe.json", "r")).keys())
    import pyprind
    ip_failed = []
    for ip in pyprind.prog_bar(ip_list):
        whois = get_org_name_by_registration_db(ip)
        print(whois)
        if whois is None:
            ip_failed.append(ip)
    print(ip_failed)
