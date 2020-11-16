import json
import re
import asyncio
import aiohttp
import time
from tqdm import tqdm


async def get(url):
    session = aiohttp.ClientSession()
    response = await session.get(url)
    result = await response.text()
    await session.close()
    return result


async def get_org_name_by_ripe(ip):
    api = "https://rest.db.ripe.net/search.json?source=ripe&query-string=%s" % ip # &source=apnic-grs
    res = await get(api)

    try:
        json_res = json.loads(res)
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


async def get_org_name_by_arin(ip):
    api = "https://whois.arin.net/rest/ip/%s.json" % ip
    res = await get(api)

    handle_json = json.loads(res)
    handle = handle_json["net"]["handle"]["$"]

    api2 = "https://whois.arin.net/rest/net/%s/pft.json?s=%s" % (handle, ip)
    res = await get(api2)

    name = None
    start_address = None
    end_address = None
    json_whois = json.loads(res)["ns4:pft"]

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


async def get_org_name_by_lacnic(ip):
    api = "https://rdap.registro.br/ip/%s" % ip
    res = await get(api)

    json_whois = json.loads(res)

    list_vcard = json_whois["entities"][0]["vcardArray"][1]
    for c in list_vcard:
        if c[0] == "fn":
            whois = c[3]
            whois["ip"] = ip
            whois["from"] = "LACNIC"
            return whois

    return None


async def get_org_name_by_apnic(ip):
    api = "http://wq.apnic.net/query?searchtext=%s" % ip
    res = await get(api)

    json_whois = json.loads(res)
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


async def get_org_name_by_registration_db(ip):
    org = await get_org_name_by_arin(ip)
    # Asia Pacific Network Information Centre, South Brisbane #

    if org is not None and "Asia Pacific Network Information Centre" in org["org_name"]:
        org = await get_org_name_by_apnic(ip)

    elif org is not None and "RIPE Network Coordination Centre" in org["org_name"]:
        org = await get_org_name_by_ripe(ip)

    elif org is not None and "Latin American and Caribbean IP address Regional Registry" in org["org_name"]:
        org = await get_org_name_by_lacnic(ip)

    elif org is None:
        return None

    # org = ner_tool.filter_out_company_char(org)

    return org


def get_org_name_by_registration_db_for_list(ip_list):
    t1 = time.time()

    # asyncio
    task_list = [get_org_name_by_registration_db(ip) for ip in ip_list]
    loop = asyncio.get_event_loop()
    finished_tasks = loop.run_until_complete(asyncio.wait(task_list))
    results = [t.result() for t in finished_tasks[0]]

    t2 = time.time()
    print("finished in {:.2} s.".format(t2 - t1))
    return results


def get_org_name_by_reg_db_friendly(ip_list, block_size = 100, sleep = 2):
    total_res = []
    for start_id in tqdm(range(0, len(ip_list), block_size)):
        block = ip_list[start_id:(start_id+block_size)]
        total_res.extend(get_org_name_by_registration_db_for_list(block))
        time.sleep(sleep)
    return total_res


if __name__ == "__main__":
    ip_list = ["154.17.24.36", "154.17.24.37", "154.17.24.39", "154.17.21.36"] * 100
    res = get_org_name_by_reg_db_friendly(ip_list)
    print(len(res))