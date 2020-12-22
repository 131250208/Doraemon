import requests
import json


def captcha_rec_3023data(captcha_bs64, format, type, api_key):
    captcha_api = "http://api.3023data.com/ocr/captcha"
    res = requests.post(captcha_api, data={
        "type": type,
        "image": "data:image/{};base64,{}".format(format, captcha_bs64),
    }, headers={
        "key": api_key,
    })
    captcha_res = json.loads(res.text)
    status = captcha_res["code"]
    if status != 0:
        print(captcha_res)
        raise Exception
    else:
        captcha_code = captcha_res["data"]["captcha"]
    return captcha_code