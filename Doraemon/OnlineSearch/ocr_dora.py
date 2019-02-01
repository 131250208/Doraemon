import base64
from urllib import parse
import requests
import json
from Doraemon import requests_dora, proxies_dora
import logging


def img_orc_google(img_url, google_api_key):
    '''
    :param img_url: http style or local path
    :return: text
    '''
    api = "https://vision.googleapis.com/v1/images:annotate?key=%s" % google_api_key
    data = {
        "requests": [
            {
                "image": {
                    "source": {
                        "imageUri": img_url,
                    }
                },
                "features": [
                    {
                        "type": "DOCUMENT_TEXT_DETECTION"
                    }
                ]
            }
        ]
    }
    if "http" not in img_url: # local path
        img = open(img_url, "rb")
        img_bs64 = base64.b64encode(img.read()).decode()
        data["requests"][0]["image"] = {"content": img_bs64}

    res = requests_dora.try_best_2_post(api, headers=requests_dora.get_default_headers(),
                                        proxies=proxies_dora.get_proxies("127.0.0.1:1080"),
                                        data=json.dumps(data), invoked_by="img_orc_google")
    if res.status_code == 200:
        json_res = json.loads(res.text)["responses"][0]
        if "error" in json_res:
            logging.warning("%s: %s" % (img_url, json_res["error"]["message"]))
            return None
        else:
            try:
                text = json_res["textAnnotations"][0]["description"]
                logging.info("google ocr success!")
                return text
            except Exception:
                return None
    logging.warning("bad response, status_code: %d" % res.status_code)
    return None


def img_orc_baidu(filePath, baidu_api, accurate=False):
    '''
    Baidu OCR API
    BAIDU_API_OCR_ACCURATE 500/d
    BAIDU_API_OCR_GENERAL 50000/d  it is bad
    :param filePath: local path
    :return: text in the image
    '''
    img = open(filePath, "rb")
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={}".format(baidu_api)
    if accurate:
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={}".format(baidu_api)
    img_bs64 = base64.b64encode(img.read()).decode()
    data = {
        "language_type": "ENG",
        "detect_direction": "true",
        "probability": "true",
        "image": img_bs64
    }
    data = parse.urlencode(data)
    res = requests.post(url, data=data)
    # print(res.text)
    return json.loads(res.text)


if __name__ == "__main__":
    text = img_orc_google("./1.tif", "AIzaSyBuvFKna_9YqhszzmGNV1MIFjGNnfz8uyk")
    print(text)