import binascii
import time
from urllib import parse
import requests
import re
import json
import logging
import base64
import random
import rsa
import logging
logging.getLogger().setLevel(logging.INFO)

import getopt
from DecryptLogin import login
import os

class WeiboRobot:
    def __init__(self, username, password):
        client = login.Client()
        weibo = client.weibo(reload_history=True)
        infos_return, weibo_session = weibo.login(username, password, mode='scanqr')
        self.nickname = infos_return.get('nick')
        self.uid = infos_return.get('uid')

        logging.info("nick: {}, uid: {}".format(self.nickname, self.uid))
        self.__session = weibo_session

        # login_info = self.__login_simulate(username, password)
        # logging.warning("login info: {}".format(login_info))
        # assert login_info is not None
        # headers = {
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        #     "Accept-Encoding": "gzip,deflate,br",
        #     "Accept-Language": "zh-CN,zh;q=0.8",
        #     "Connection": "keep-alive",
        #     "Host": "weibo.com",
        #     "Referer": "https://weibo.com/",
        #     "Upgrade-Insecure - Requests": "1",
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
        # }
        #
        # self.__session.headers.update(headers)

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            "x-xsrf-token": "ca8f34",
            # "cookie": "_T_WM=95408813990; XSRF-TOKEN=ca8f34; SCF=AvAoiM-KriYpOE7doKShZInAbXDWWZNF2LALSnsH7OKum4ytQ30c_ymO7WpHP1Zt4EOkNaeFawbBlpQjRPQ4yoM.; SUB=_2A25Pa7GDDeRhGeFJ61YR-CnEzTSIHXVsl9_LrDV6PUJbktCOLXbNkW1NfKbZ-gLFw-TULujLZsmu8bvgIK35TFs1; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFMOSlN8oDRwUroYf4GTYxo5NHD95QNS05XehnN1hqRWs4Dqcjki--NiKy8iKyFi--4iKLFi-2Ri--fiKLsiKy8Bg4.wBtt; WEIBOCN_FROM=1110006030; MLOGIN=1; SSOLoginState=1651491369; M_WEIBOCN_PARAMS=lfid=102803&luicode=20000174&uicode=20000174; mweibo_short_token=7674ff4669",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        }
        # 设置一个会话给m.weibo.cn，weibo.com登录并不能同步状态到m.weibo.cn，mweibo用cookie
        self.mweibo_session = requests.Session()
        # self.mweibo_session.get(url, headers=headers)  # do not forget to set the cookie

    def __prelogin(self, username_encoded):
        url = "http://login.sina.com.cn/sso/prelogin.php"
        payload = {
            "entry": "weibo",
            "callback": "sinaSSOController.preloginCallBack",
            "su": username_encoded,
            "rsakt": "mod",
            "checkpin": "1",
            "client": "ssologin.js(v1.4.19)",
            "_": int(time.time() * 1000),
        }
        res = self.__session.post(url, data=payload, )
        prelogin_json = re.search("\((.*)\)", res.text).group(1)

        return json.loads(prelogin_json)

    def __get_username(self, username):
        return base64.b64encode(parse.quote_plus(username).encode("utf-8"))

    def __get_password(self, pass_word, servertime, nonce, pubkey):
        string = (str(servertime) + "\t" + str(nonce) + "\n" + str(pass_word)).encode("utf-8")
        public_key = rsa.PublicKey(int(pubkey, 16), int("10001", 16))
        password = rsa.encrypt(string, public_key)
        password = binascii.b2a_hex(password)
        return password.decode()

    def __identify_captcha(self, cap_b64):
        typeid = 35
        appkey = "f1d9b361016be2d78f0684fb5891f2c3"
        url = "https://way.jd.com/showapi/checkcode_ys?typeId=%d&convert_to_jpg=0&appkey=%s" % (typeid, appkey)

        payload = {
            "body": "img_base64=%s" % cap_b64,
        }
        res = requests.post(url, data=payload)
        res_js = res.json()
        if res_js["code"] == "10000" and res_js["result"]["showapi_res_code"] == 0 and \
                        res_js["result"]["showapi_res_body"]["ret_code"] == 0:
            return res_js["result"]["showapi_res_body"]["Result"]
        else:
            logging.warning(res_js)
            return None

    def __login_request(self, username_encoded, pw_encrypted, prelogin_json):
        url_login = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&wsseretry=servertime_error"
        payload = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "userticket": "1",
            "vsnf": "1",
            "service": "miniblog",
            "encoding": "UTF-8",
            "pwencode": "rsa2",
            "sr": "1280*800",
            "prelt": "529",
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "rsakv": prelogin_json["rsakv"],
            "servertime": prelogin_json["servertime"],
            "nonce": prelogin_json["nonce"],
            "su": username_encoded,
            "sp": pw_encrypted,
            "returntype": "TEXT",
        }

        # 判断验证码
        json_ticket = None
        if "showpin" in prelogin_json and prelogin_json["showpin"] == 1:  # 如果需要输入验证码
            payload["pcid"] = prelogin_json["pcid"]

            url_pin = "http://login.sina.com.cn/cgi/pin.php?r=%d&s=0&p=%s" % (
                int(time.time() * 1000), prelogin_json["pcid"])  # 获得验证码的地址

            res = self.__session.post(url_pin, data=payload)
            captcha_img = open("./captcha.png", "wb")
            captcha_img.write(res.content)
            captcha_img.close()

            captcha_img_b64 = base64.b64encode(res.content).decode()
            iden = self.__identify_captcha(captcha_img_b64)

            code = ""
            if iden is None:
                code = input("请输入验证码:")
            else:
                code = iden

            payload["door"] = code

        # login weibo.com
        res = self.__session.post(url_login, data=payload)
        json_ticket = res.json()
        if json_ticket["retcode"] != "0":
            logging.warning("WeiBoLogin failed: %s", json_ticket)
            return False
        else:
            params = {
                "callback": "sinaSSOController.callbackLoginStatus",
                "client": "ssologin.js(v1.4.19)",
                "ticket": json_ticket["ticket"],
                "ssosavestate": int(time.time()),
                "_": int(time.time() * 1000),
            }
            response = self.__session.get("http://passport.weibo.com/wbsso/login", params=params)
            json_data_2 = json.loads(re.search(r"\((?P<result>.*)\)", response.text).group("result"))
            if json_data_2["result"] is True:
                self.__uid = json_data_2["userinfo"]["uniqueid"]
                self.__user_nick = json_data_2["userinfo"]["displayname"]
                logging.warning("WeiBoLogin succeed: %s", json_data_2)
                return True
            else:
                logging.warning("WeiBoLogin failed: %s", json_data_2)
                return False

    def __is_home(self):
        res = self.__session.get("https://weibo.com/u/%s/home" % (self.__uid)).text
        if u"我的首页" in res:
            return True
        else:
            return False

    def __login_simulate(self, username, pw):
        max_times = 5
        count_login = 0
        while True:
            username_encoded = self.__get_username(username)
            prelogin_json = self.__prelogin(username_encoded)
            pw_encrypted = self.__get_password(pw, prelogin_json["servertime"], prelogin_json["nonce"],
                                               prelogin_json["pubkey"])

            login_res = self.__login_request(username_encoded, pw_encrypted, prelogin_json)
            if login_res and self.__is_home():  # 一旦登录成功就返回user
                return {"uid": self.__uid, "session": self.__session}  # 返回登录的user的dict
            else:
                count_login += 1
                if count_login == max_times:
                    logging.warning("exceeded the max times of login...")
                    return None
                logging.warning("%s login failed, try again..." % username)
                random.seed(time.time())
                sleeptime = 5 * random.random()
                logging.warning("sleep %ds" % sleeptime)
                time.sleep(sleeptime)

    # api for users
    # ------------------------------------------------------------------------------------------------------
    def edit_profile(self):
        '''
        edit profile
        :return:
        '''
        payload = {
            'setting_rid': 'd1Vlf235Q-LBj/DshHM8stx-1GQ=',
            'nickname': '睡小迪_爱琪琪阿四',
            'realname': '薛梦雪',
            'gender': 'f',
            'sextrend[]': '0',
            'blog': '',
            'mydesc': '一心一意',
            'province': '11',
            'city': '1',
            'love': '',
            'Date_Year': '1998',
            'birthday_m': '03',
            'birthday_d': '06',
            'blood': '',
            'pub_name': '0',
            'pub_sextrend': '0',
            'pub_love': '1',
            'pub_birthday': '3',
            'pub_blood': '1',
            'pub_blog': '2',
        }
        res = self.__session.post("https://account.weibo.com/set/aj/iframe/editinfo",
                                  headers={"Host": "account.weibo.com", }, data=payload).text
        if res['code'] == '100000':
            print("edit_profile success!")
            return True
        else:
            print("edit_profile fail... " + res['msg'])
            return False

    def edit_edu(self):
        '''
        edit education
        :return:
        '''
        payload = {'name': '北京外国语大学',
                   'school_type': '1',
                   'start': '2014',
                   'privacy': '2',
                   'school_province': '11',
                   'school_id': '243973',
                   }

        res = self.__session.post("https://account.weibo.com/set/aj/iframe/edupost",
                                  headers={"Host": "account.weibo.com", }, data=payload).text
        try:
            res = json.loads(res)
            if res['code'] == '100000':
                print("edit_edu success!")
                return True
            else:
                print("edit_edu fail... " + res['msg'])
                return False
        except:
            print(res)
            return False

    # def post(self, text, img_url_list=None, img_id_list=None):
    #     '''
    #     post text
    #     :param text:
    #     :return:
    #     '''
    #     payload = {
    #         'text': text,
    #         'appkey': '',
    #         'style_type': '1',
    #         'pic_id': '',
    #         'tid': '',
    #         'pdetail': '',
    #         'rank': '0',
    #         'rankid': '',
    #         'module': 'stissue',
    #         'pub_source': 'main_',
    #         'pub_type': 'dialog',
    #         'isPri': '0',
    #         '_t': '0',
    #     }
    #
    #     if img_id_list is None and img_url_list is not None:
    #         img_id_list = []
    #         for url in img_url_list:
    #             img_id = self.__up_img(url)
    #             if img_id is not None:
    #                 img_id_list.append(img_id)
    #
    #     if img_id_list is not None:
    #         pic_id = "|".join(img_id_list)
    #         payload["pic_id"] = pic_id
    #
    #     res = self.__session.post("https://weibo.com/aj/mblog/add", data=payload).text
    #     res = json.loads(res)
    #     if res['code'] == '100000':
    #         logging.warning("post blog success!")
    #         return True
    #     else:
    #         logging.warning("post blog fail... " + res['msg'])
    #         return False

    def upload_pic(self, pic_path):
        picture = open(pic_path, "rb").read()
        url = 'https://picupload.weibo.com/interface/pic_upload.php'
        params = {
            'data': '1',
            'p': '1',
            'url': 'weibo.com/u/%s' % self.uid,
            'markpos': '1',
            'logo': '1',
            'nick': '@%s' % self.nickname,
            'marks': '1',
            'app': 'miniblog',
            's': 'json',
            'pri': 'null',
            'file_source': '1'
        }
        res = self.__session.post(url, headers=self.headers, params=params, data=picture)
        res_json = res.json()
        if res_json['code'] == 'A00006':
            pid = res_json['data']['pics']['pic_1']['pid']
            return pid
        else:
            logging.warning("upload pic failed...")
            return None

    def post(self, text, pic_path_list=None, rank=0):
        '''
        post a blog
        :param text:
        :param pictures:
        :return:
        '''
        # 上传图片
        if pic_path_list is None:
            pic_path_list = []
        pic_ids = []
        for pic_path in pic_path_list:
            pid = self.upload_pic(pic_path)
            time.sleep(random.random() + 0.5)
            pic_ids.append(pid)

        pic_ids = [idx for idx in pic_ids if idx is not None]
        # 发微博
        url = 'https://www.weibo.com/aj/mblog/add?ajwvr=6&__rnd=%d' % int(time.time() * 1000)
        data = {
            'title': '',
            'location': 'v6_content_home',
            'text': text,
            'appkey': '',
            'style_type': '1',
            'pic_id': '|'.join(pic_ids),
            'tid': '',
            'pdetail': '',
            'mid': '',
            'isReEdit': 'false',
            'gif_ids': '',
            'rank': str(rank),  # 0 公开, 1自己可见, 6好友圈
            'rankid': '',
            'pub_source': 'page_2',
            'topic_id': '',
            'updata_img_num': str(len(pic_ids)),
            'pub_type': 'dialog'
        }
        headers = self.headers.copy()
        headers.update({'Referer': 'http://www.weibo.com/u/%s/home?wvr=5' % self.uid})
        res = self.__session.post(url, headers=headers, data=data)
        is_success = False
        if res.status_code == 200:
            is_success = True
        return is_success

    def like_blog(self, blog_mid):
        '''
        like a blog
        :param blog_mid:
        :return:
        '''
        payload = {
            'version': ' mini',
            'qid': ' heart',
            'mid': blog_mid,
            'loc': ' profile',
            'cuslike': ' 1',
            '_t': ' 0',
        }
        res = self.__session.post("https://weibo.com/aj/v6/like/add", data=payload).text

        try:
            res = json.loads(res)
            if res['code'] == '100000':
                logging.warning("%s like_blog %s success!" % (self.__uid, blog_mid))
                return True
            else:
                logging.warning("%s like_blog %s fail... msg: %s" % (self.__uid, blog_mid, res['msg']))
                return False
        except:
            logging.warning("%s like_blog %s fail... msg: %s" % (self.__uid, blog_mid, res))
            return False

    #
    def like_object(self, ob_id, ob_type):
        payload = {
            'object_id': ob_id,
            'object_type': ob_type,
            '_t': '0',
        }
        res = self.__session.post("https://weibo.com/aj/v6/like/objectlike", data=payload).text
        res = json.loads(res)
        if res['code'] == '100000':
            logging.warning("like_object(%s) success!" % (ob_type))
            return True
        else:
            logging.warning("like_object(%s) fail... " % (ob_type) + res['msg'])
            return False

    def like_comment(self, comment_id):
        '''
        like a comment
        :param comment_id:
        :return:
        '''
        self.like_object(comment_id, "comment")

    # 评论和转发
    def comment_forward(self, blog_mid, text, forward=False, img_url=None, img_id=None):  # 目标微博id, 评论者的uid，评论内容，forward = {"0", "1"}是否转发
        '''
        send a comment and forward it
        :param blog_mid: the id of the target comment
        :param text: what you wanna send
        :param forward: forward it or not
        :param img_url: set the url of a image if you wanna send one
        :param img_id: set if you wanna send an existing image(if you have upload an image to the Weibo,
                there would be an id for it
        :return:
        '''
        payload = {
            'act': 'post',
            'mid': blog_mid,
            'uid': self.uid,
            'isroot': '0',
            'content': text,
            'module': 'scommlist',
            'group_source': '',
            '_t': '0',
            "forward": "1" if forward else "0",
        }

        if img_url is not None:
            pic_id = self.__up_img(img_url)
            payload["pic_id"] = pic_id
        if img_id is not None:
            payload["pic_id"] = img_id

        url = "https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=%d" % int(time.time() * 1000)

        headers = self.headers.copy()
        headers.update({'Referer': 'http://www.weibo.com/u/%s/home?wvr=5' % self.uid})
        res = self.__session.post(url, headers=headers, data=payload)

        try:
            res = json.loads(res.text)
            if res['code'] == '100000':
                logging.info("comment_forward success! comment: %s" % text)
                return True
            else:
                logging.info("%s comment_forward %s fail... code: %s msg: %s" % (
                    self.__uid, blog_mid, res['code'], res['msg']))
        except Exception as e:
            logging.warning(e)

        return False

    def reply_comment(self, blog_mid, comment_id, text, approval=False
                      , forward=False, img_path=None):
        '''
        reply a comment, the args are the same as function comment_forward
        :param blog_mid:
        :param comment_id:
        :param text:
        :param approval:
        :param forward:
        :param img_url:
        :param img_id:
        :return:
        '''
        payload = {
            "act": "reply",
            "canUploadImage": "1",
            "cid": comment_id,
            "content": text,
            "dissDataFromFeed": "[object Object]",
            "ispower": "1",
            "isroot": "0",
            "approvalComment": "true" if approval else "false",
            # "location": "page_100505_home",
            "forward": "1" if forward else "0",
            "mid": blog_mid,
            "module": "scommlist",
            "nick": self.nickname,
            # "ouid": "2887964854",
            # "pdetail": "1005056219737121",
            # "root_comment_id": "4221420517644305",
            # "status_owner_user": "6219737121",
            "uid": self.uid,
        }

        if img_path is not None:
            pic_id = self.upload_pic(img_path)
            payload["pic_id"] = pic_id if pic_id is not None else ""

        url = "https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=%d" % int(time.time() * 1000)
        headers = self.headers.copy()
        headers.update({'Referer': 'http://www.weibo.com/u/%s/home?wvr=5' % self.uid})
        res = self.__session.post(url, headers=headers, data=payload)

        try:
            res = json.loads(res.text)
            if res['code'] == '100000':
                logging.warning("comment_forward success! reply: %s" % text)
                return True
            else:
                logging.warning(
                    "%s comment_forward %s fail... code: %s msg: %s" % (
                        self.uid, comment_id, res['code'], res['msg']))
        except Exception as e:
            print("it is not json")
            logging.warning(e)

        return False

    def get_comments_data(self, mid):
        batch_size = 200
        comments_url = "https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id={}&is_show_bulletin=2&is_mix=0&count={}&uid={}".format(
            mid, batch_size, self.uid)

        while True:
            try:
                res = self.__session.get(comments_url)
                res_dict = json.loads(res.text)
                if res_dict["ok"] == 1:
                    break
            except Exception as e:
                logging.warning("获取评论失败，重试")
                pass

        comments_data = []
        comments_data.extend(res_dict["data"])

        while res_dict["max_id"] != 0:
            comments_url = "https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id={}&is_show_bulletin=2&is_mix=0&max_id={}&count={}&uid={}".format(
                mid, res_dict["max_id"], batch_size, self.uid)
            while True:
                try:
                    res = self.__session.get(comments_url)
                    res_dict = json.loads(res.text)
                    if res_dict["ok"] == 1:
                        break
                except Exception as e:
                    logging.warning("获取评论失败，重试")
                    pass

            if len(res_dict["data"]) > 0:
                comments_data.extend(res_dict["data"])
            elif res_dict["trendsText"] == "已加载全部评论":
                break

        return comments_data

    def __img_bs64(self, url):
        '''
        image to base64 encoding
        :param url:
        :return:
        '''
        ls_f = ""
        if "http" in url:  # 网络地址
            content = requests.get(url).content
            ls_f = base64.b64encode(content)  # 读取文件内容，转换为base64编码

        else:  # 本地地址
            f = open(url, 'rb')  # 二进制方式打开图文件
            ls_f = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
            f.close()
        img_bs64_str = ls_f.decode()  # 解码成字符串

        return img_bs64_str

    def __up_img(self, img_url):
        '''
        upload img and get img id
        :param img_url:
        :return:
        '''
        img_bs64_str = self.__img_bs64(img_url)

        url = "https://picupload.weibo.com/interface/pic_upload.php"
        payload = {
            "cb": "https://weibo.com /aj/static/upimgback.html?_wv=5&callback=STK_ijax_151694642763479",
            "mime": "image/jpeg",
            "data": "base64",
            "url": "weibo.com/u/%s" % self.__uid,
            "markpos": "1",
            "logo": "1",
            # "nick": "@王雨城_Vision_Wong",
            "marks": "1",
            "app": "miniblog",
            "s": "rdxt",
            "file_source": "3",
        }

        img = {
            "b64_data": img_bs64_str,
        }
        try:
            res = self.__session.post(url, data=payload, files=img)
        except Exception as e:
            se = re.search("&pid=([\S]*)", str(e))
            if se is None:
                return None
            img_id = se.group(1)
            return img_id

    def del_blog(self, blog_mid):
        '''
        delete a blog
        :param blog_mid:
        :return:
        '''
        payload = {
            'mid': blog_mid,
        }
        res = self.__session.post("https://weibo.com/aj/mblog/del", data=payload).text
        res = json.loads(res)
        if res['code'] == '100000':
            print("mblog %s del_blog success!" % blog_mid)
            return True
        else:
            print("mblog %s del_blog fail... " % blog_mid + res['msg'])
            return False

    def del_comment(self, blog_mid, comment_id):
        '''
        delete a comment under your post
        :param blog_mid:
        :param comment_id:
        :return:
        '''
        payload = {
            'act': 'delete',
            'mid': blog_mid,
            'cid': comment_id,
            'uid': self.__uid,
            'is_block': '0',
            'rid': comment_id,
            'oid': '',
            '_t': '0',
        }
        res = self.__session.post("https://weibo.com/aj/comment/del", data=payload).text
        res = json.loads(res)
        if res['code'] == '100000':
            print("del_comment success!")
            return True
        else:
            print("del_comment fail... " + res['msg'])
            return False

    def follow_unfo(self, object_uid, follow):
        '''
        follow or unfollow someone
        :param object_uid:
        :param follow: boolean
        :return:
        '''
        payload = {
            'uid': object_uid,
            'refer_flag': '1005050002',
            'oid': object_uid,
            'wforce': '1',
            'nogroup': 'false',
            'refer_from': 'profile_headerv6',
            '_t': '0',
        }
        follow = "followed" if follow == "1" else "unfollow"

        res = self.__session.post("https://weibo.com/aj/f/%s" % (follow), data=payload).text
        res = json.loads(res)
        if res['code'] == '100000':
            print("follow_unfo success!")
            return True
        else:
            print("follow_unfo fail... " + res['msg'])
            return False

    def home(self):
        res = self.__session.get("https://weibo.com/u/%s/home" % (self.__uid)).text
        # print(res)
        if u"我的首页" in res:
            return True
        else:
            return False

    # 进入微博等级页面再回到主页，等级可升到4级
    def check_level(self):
        for i in range(3):
            self.__session.get("http://level.account.weibo.com/level/mylevel?from=front",
                               headers={"Host": "level.account.weibo.com"})
        self.home()

    def __interface_4_all_instructions(self, instruction_name, **kwargs):
        if instruction_name == "comment_forward":
            img_url = kwargs["img_url"] if "img_url" in kwargs else None
            img_id = kwargs["img_id"] if "img_id" in kwargs else None
            forward = kwargs["forward"] if "forward" in kwargs else False
            self.comment_forward(kwargs["blog_mid"], kwargs["text"], forward, img_url, img_id)
        if instruction_name == "post":
            img_url_list = kwargs["img_url_list"] if "img_url_list" in kwargs else None
            img_id_list = kwargs["img_id_list"] if "img_id_list" in kwargs else None
            self.post(kwargs["text"], img_url_list, img_id_list)
        if instruction_name == "like_blog":
            self.like_blog(kwargs["blog_mid"])
        if instruction_name == "like_comment":
            self.like_comment(kwargs["comment_id"])
        if instruction_name == "follow_unfo":
            self.follow_unfo(kwargs["object_uid"], kwargs["follow"])
        if instruction_name == "reply_comment":
            img_url = kwargs["img_url"] if "img_url" in kwargs else None
            img_id = kwargs["img_id"] if "img_id" in kwargs else None
            approval = kwargs["approval"] if "approval" in kwargs else False
            forward = kwargs["forward"] if "forward" in kwargs else False
            self.reply_comment(kwargs["blog_mid"], kwargs["comment_id"], kwargs["text"], approval, forward, img_url, img_id)
        if instruction_name == "del_blog":
            self.del_blog(kwargs["blog_mid"])
        if instruction_name == "del_comment":
            self.del_comment(kwargs["blog_mid"], kwargs["comment_id"])

    def shell(self):
        logging.warning("shell ...")
        while True:
            argv = input()
            if argv == "exit":
                break
            argv = argv.split(" ")
            parameters = ["blog_mid=", "forward=", "img_url=", "img_id=", "text=", "img_url_list=",
                          "img_id_list=", "comment_id=", "object_uid=", "approval="]
            options, args = getopt.getopt(argv, "i:", parameters)
            parameters_inp = ["--{}".format(p.rstrip("=")) for p in parameters]

            instruction_name = ""
            parameters_dict = {}
            for opt, arg in options:
                if opt == "-i":
                    instruction_name = arg
                    print("instruction: {}".format(arg))
                if opt in parameters_inp:
                    if arg == "True":
                        arg = True
                    if arg == "False":
                        arg = False
                    if arg == "None":
                        arg = None

                    if opt == "--img_url_list" or opt == "--img_id_list":
                        arg = arg.split("|")
                    parameters_dict[re.search("--(.*)", opt).group(1)] = arg
            try:
                self.__interface_4_all_instructions(instruction_name, **parameters_dict)
            except Exception as e:
                logging.warning("sth went wrong, {}".format(e))


def monitor_reply_gaokao_en(blog_id, mem_path="./query.mem"):
    mem_list = list()
    if mem_path is not None:
        with open(mem_path, "r", encoding="utf-8") as file_in:
            for line in file_in:
                mem_list.append(line.strip("\n"))

    weibo_robot = WeiboRobot("13120178370", "Weibo6981228.")
     # "4775107736111803"
    memory_set = set(mem_list)
    wish = ["高考加油！",
            "祝考试顺利",
            "祝高考成功",
            "祝金榜题名!",
            "祝你圆梦理想的大学",
            "祝考上心仪的学校",
            "加油，等你好消息！"]
    while True:
        comments = weibo_robot.get_comments_data(blog_id)
        for com in comments:
            com_txt = re.sub("\[.*?\]", " ", com["text_raw"])
            com_txt = re.sub("https?://[^\s]*", " ", com_txt)
            com_txt = re.sub("@[a-zA-Z]+", " ", com_txt)

            for word in re.findall("[a-zA-Z]+", com_txt):
                mem = "{},{}".format(com["user"]["id"], word)
                if mem not in memory_set:
                    img_path = "src/shs_words/{}.png".format(word)
                    if os.path.exists(img_path):
                        res = weibo_robot.reply_comment(blog_id, com["id"], "{}, {}".format(word, random.choice(wish)),
                                                  img_path=img_path)
                    else:
                        res = weibo_robot.reply_comment(blog_id, com["id"], "暂未收录该词：{}，请检查拼写".format(word))
                    if res is True:
                        memory_set.add(mem)
                    with open(mem_path, "a", encoding="utf-8") as file_out:
                        file_out.write("{}\n".format(mem))
                    time.sleep(random.random() + 1)
        time.sleep(random.random() + 0.8)


if __name__ == "__main__":
    monitor_reply_gaokao_en("4775292251410441")

    # weibo_robot.post("test send_weibo", pic_path_list=["./test2.png", ], rank=1)
    # weibo_robot.reply_comment("4775107736111803", "4775110336577568", "reply wyc!")
    # weibo_robot.reply_comment("4773718829566516", "4773726883415094", "test")

    # feedback = weibo_robot.post("Robot Test...", img_url_list=["test1.png", "test2.png"])

    # '''
    # -i post --text=HellowWorld --img_url_list=test1.png|test2.png
    # -i comment_forward --blog_mid=4321252124398928 --text=heyguys --forward=True --img_url=test1.png
    # -i like_blog --blog_mid=4321252124398928
    # -i like_comment --comment_id=4321252828681425
    # -i reply_comment --blog_mid=4321252124398928 --comment_id=4321252828681425 --text=reply_comment --img_url=test1.png
    # -i del_comment --blog_mid=4321252124398928 --comment_id=4321252828681425
    # -i del_blog --blog_mid=4321252124398928
    # '''
    # weibo_robot.shell()