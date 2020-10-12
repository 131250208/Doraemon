#-*- coding: utf-8 -*-
import html
import json
import re
import os
from urllib import parse
from Doraemon.Requests import requests_dora
from tqdm import tqdm

def get_album_list(sin, ein):
    url = "https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg"
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "cookie": "RK=7dNm4/X + Yj; tvfe_boss_uuid=bf00ee54e9081ab4; pgv_pvi=8772238336; pac_uid=1_857193777; pgv_pvid=6457341280; o_cookie=80; ptcz=c761e59c8c8d6bd5198866d02a5cb7313af1af468006c455d6c2b5d26201d42e; pgv_si=s10759168; _qpsvr_localtk=0.08285763449905015; ptisp=ctc; luin=o0857193777; lskey=00010000228dd1371b945c68ecfd3b71d3071425024a7a8a2a23e3ffcb5b9904c9f7088d2ea8c01539ffed92; pt2gguin=o0857193777; uin=o0857193777; skey=@Kydi7w0EI; p_uin=o0857193777; p_skey=HjsE9sEjznJfXk*9KFEeW4VZr6i3*tlXZ2nuzEw8kCg_; pt4_token=c-p6sv3JEboA51cSQ3ABqxM8O80Jct3jYYkgy-aEQuE_; p_luin=o0857193777; p_lskey=000400008f9c296cd10c03a5173d22a184aad124d791568e90e4198beb8ad699a4d02fbfc059f71ab3d8758c; ts_last=y.qq.com/portal/playlist.html; ts_refer=ui.ptlogin2.qq.com/cgi-bin/login; ts_uid=3392060960",
        "referer": "https://y.qq.com/portal/playlist.html"
    }
    paramter = {
        "g_tk": "1089387893",
        "jsonpCallback": "getPlaylist",
        "loginUin": "0",
        "hostUin": "0",
        "format": "jsonp",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": "0",
        "platform": "yqq",
        "needNewCode": "0",
        "categoryId": "10000000",
        "sortId": "5",
        "sin": sin, # 开始结点
        "ein": ein # 结束结点，用于翻页
    }
    html_text = requests_dora.try_best_2_get(url=url, params=paramter, headers=header).text
    res = json.loads(html_text.lstrip("getPlaylist(").rstrip(")"))["data"]["list"]
    album_list = []

    for t_item in res:
        album = {}
        ILLEGAL_CHARACTERS_RE = re.compile(r"[\000-\010]|[\013-\014]|[\016-\037]")#用于去掉非法字符
        album["createtime"] = t_item["createtime"]
        album["creator_qq"] = t_item["creator"]["qq"]
        album["creator_name"] = t_item["creator"]["name"]
        album["creator_name"] = ILLEGAL_CHARACTERS_RE.sub(r"",  album["creator_name"])
        album["creator_isVip"] = t_item["creator"]["isVip"]
        album["dissid"] = t_item["dissid"] #提取歌单id，用于后续提取歌曲id
        album["dissname"] = t_item["dissname"] #歌单名称
        album["dissname"] = ILLEGAL_CHARACTERS_RE.sub(r"",  album["dissname"])
        album["listennum"] = t_item["listennum"] #播放量
        album_list.append(album)
    return album_list


#爬取歌曲id
def get_song_list(dissid):
    url = "https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg"
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "cookie": "RK=7dNm4/X + Yj; tvfe_boss_uuid=bf00ee54e9081ab4; pgv_pvi=8772238336; pac_uid=1_857193777; pgv_pvid=6457341280; o_cookie=857193777; ptcz=c761e59c8c8d6bd5198866d02a5cb7313af1af468006c455d6c2b5d26201d42e; pgv_si=s10759168; _qpsvr_localtk=0.08285763449905015; ptisp=ctc; luin=o0857193777; lskey=00010000228dd1371b945c68ecfd3b71d3071425024a7a8a2a23e3ffcb5b9904c9f7088d2ea8c01539ffed92; pt2gguin=o0857193777; uin=o0857193777; skey=@Kydi7w0EI; p_uin=o0857193777; p_skey=HjsE9sEjznJfXk*9KFEeW4VZr6i3*tlXZ2nuzEw8kCg_; pt4_token=c-p6sv3JEboA51cSQ3ABqxM8O80Jct3jYYkgy-aEQuE_; p_luin=o0857193777; p_lskey=000400008f9c296cd10c03a5173d22a184aad124d791568e90e4198beb8ad699a4d02fbfc059f71ab3d8758c; ts_last=y.qq.com/portal/playlist.html; ts_refer=ui.ptlogin2.qq.com/cgi-bin/login; ts_uid=3392060960",
        "referer": "https://y.qq.com/n/yqq/playlist/{}.html".format(dissid)
    }
    paramters = {
        "type": "1",
        "json": "1",
        "utf8": "1",
        "onlysong": "0",
        "disstid": dissid,
        "format": "jsonp",
        "g_tk": "1089387893",
        "jsonpCallback": "playlistinfoCallback",
        "loginUin": "857193777",
        "hostUin": "0",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": 0,
        "platform": "yqq",
        "needNewCode": 0
    }
    html_text = requests_dora.try_best_2_get(url=url, params=paramters, headers=header).text
    cdlist = json.loads(html_text.lstrip("playlistinfoCallback(").rstrip(")"))["cdlist"]
    if len(cdlist) >= 1:
        cdlist = cdlist[0]
    song_list = []

    tags = ", ".join([i["name"] for i in cdlist["tags"]])
    for item in cdlist["songlist"]:
        song = {}
        # if "size128" in item:
        #     song["size128"] = item["size128"]
        if "songmid" in item:
            song["songmid"] = item["songmid"]
        else:
            continue

        if "songid" in item:
            song["songid"] = item["songid"]
        else:
            continue

        song["albumname"] = item["albumname"]
        song["songname"] = item["songname"]
        song["singer"] = ", ".join([i["name"] for i in item["singer"]])
        song["tags"] = tags
        song_list.append(song)
    return song_list


def get_lyric(song):
    songid = song["songid"]
    songmid = song["songmid"]
    url = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric.fcg"
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "referer": "https://y.qq.com/n/yqq/song/{}.html".format(songmid)
    }
    paramters = {
        "nobase64": 1,
        "musicid": songid,
        "callback": "jsonp1",
        "g_tk": "1134533366",
        "jsonpCallback": "jsonp1", 
        "loginUin": "0",
        "hostUin": "0",
        "format": "jsonp",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": "0",
        "platform": "yqq",
        "needNewCode": "0"
    }
    html_text = requests_dora.try_best_2_get(url=url, params=paramters, headers=header).text
    res = json.loads(html_text.lstrip("jsonp1(").rstrip(")"))
    # if "lyric" in res:
    #     lyric = res["lyric"]
    #     # decode
    #     lyric = html.unescape(lyric)
    #     lyric = html.unescape(lyric)
    #     lyric = parse.unquote(lyric)
    #
    #     it = re.finditer(r"\[(.*?)\](.+)", lyric)
    #     lyric_lines = []
    #     for match in it:
    #         time_pop_up = match.group(1)
    #         time_split = time_pop_up.split(".")
    #         ms = float("0.{}".format(time_split[1]))
    #         sec = time.strptime(time_split[0], "%M:%S").tm_sec
    #         line = match.group(2)
    #         line = line.strip()
    #         if re.search("[:：]", line) or line == "" or line == "此歌曲为没有填词的纯音乐，请您欣赏":
    #             continue
    #         lyric_lines.append({
    #             "time": sec + ms,
    #             "line": line,
    #         })
    #
    #     return lyric_lines[1:]
    # else:
    #     return []
    if "lyric" in res:
        lyric = res["lyric"]
        if "此歌曲为没有填词的纯音乐，请您欣赏" in lyric:
            return {}, []
        # decode
        lyric = html.unescape(lyric)
        lyric = html.unescape(lyric)
        lyric = parse.unquote(lyric)

        it = re.finditer(r"\[(\d+):(\d+.\d+)\](.+)", lyric)
        lyric_lines = []
        contributors_dict = {}
        for match in it:
            min = float(match.group(1))
            try:
                sec = float(match.group(2))
            except ValueError:
                sec = 0

            line = match.group(3)
            line = line.strip()
            if line == "":
                continue
            se_contributors = re.search("(.*?)[:：](.*)", line)
            if se_contributors:
                contributors_dict[se_contributors.group(1).strip()] = se_contributors.group(2).strip()
                continue
            lyric_lines.append({
                "time": min * 60 + sec,
                "line": line,
            })

        return contributors_dict, lyric_lines[1:]
    else:
        return {}, []


def get_detail(song):
    songid = song["songid"]
    songmid = song["songmid"]

    url = "https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg"
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "referer": "https://y.qq.com/n/yqq/song/{}.html".format(songid)
    }
    paramters = {
        "songmid": songmid,
        "tpl": "yqq_song_detail",
        "format": "jsonp",
        "callback": "getOneSongInfoCallback",
        "g_tk": "1134533366",
        "jsonpCallback": "getOneSongInfoCallback",
        "loginUin": "0",
        "hostUin": "0",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": 0,
        "platform": "yqq",
        "needNewCode": 0
    }
    html_text = requests_dora.try_best_2_get(url=url, params=paramters, headers=header, verify=True).text
    detail = json.loads(html_text.lstrip("getOneSongInfoCallback(").rstrip(")"))["data"]
    song = {}
    if len(detail) > 0:
        detail = detail[0]
        song["subtitle"] = detail["subtitle"]
        song["title"] = detail["title"]
        song["time_public"] = detail["time_public"]
        try:
            song["url"] = json.loads(html_text.lstrip("getOneSongInfoCallback(").rstrip(")"))["url"][str(songid)]
        except:
            song["url"] = ""
    return song


if __name__ == "__main__":
    save_path = "./qq_music_songs_by_album"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    for sin in range(0, 7050, 30):
        ein = sin + 29
        album_list = get_album_list(sin, ein) # get 30 albums

        for album in album_list:
            dissname = album["dissname"]
            song_list = get_song_list(album["dissid"])
            chunk = []
            for song in tqdm(song_list, desc = "getting songs in {}".format(dissname)):
                contributors, lyric = get_lyric(song)
                song["lyric"] = lyric
                chunk.append(song)

            json.dump(chunk, open("{}/lyric_{}.json".format(save_path, dissname), "w", encoding = "utf-8"), ensure_ascii = False)

