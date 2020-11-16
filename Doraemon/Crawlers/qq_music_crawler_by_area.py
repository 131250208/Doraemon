import html
import json
import math
import os
import re
from urllib import parse
from tqdm import tqdm
from Doraemon.Requests import requests_dora

KEY_LYRIC = "lyric"
KEY_CONTRIBUTORS = "contributors"
KEY_SINGER_NAME = "singer_name"
KEY_SINGER_ID = "singer_id"
KEY_SINGER_MID = "singer_mid"

def get_singer_list_page(area_id, page_ind):
    '''

    :param area_id: {'全部': -100, '内地': 200, '港台': 2, '欧美': 5, '日本': 4, '韩国': 3, '其他': 6}
    :param page_ind:
    :return:
    '''
    url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "cookie": "RK=7dNm4/X + Yj; tvfe_boss_uuid=bf00ee54e9081ab4; pgv_pvi=8772238336; pac_uid=1_857193777; pgv_pvid=6457341280; o_cookie=857193777; ptcz=c761e59c8c8d6bd5198866d02a5cb7313af1af468006c455d6c2b5d26201d42e; pgv_si=s10759168; _qpsvr_localtk=0.08285763449905015; ptisp=ctc; luin=o0857193777; lskey=00010000228dd1371b945c68ecfd3b71d3071425024a7a8a2a23e3ffcb5b9904c9f7088d2ea8c01539ffed92; pt2gguin=o0857193777; uin=o0857193777; skey=@Kydi7w0EI; p_uin=o0857193777; p_skey=HjsE9sEjznJfXk*9KFEeW4VZr6i3*tlXZ2nuzEw8kCg_; pt4_token=c-p6sv3JEboA51cSQ3ABqxM8O80Jct3jYYkgy-aEQuE_; p_luin=o0857193777; p_lskey=000400008f9c296cd10c03a5173d22a184aad124d791568e90e4198beb8ad699a4d02fbfc059f71ab3d8758c; ts_last=y.qq.com/portal/playlist.html; ts_refer=ui.ptlogin2.qq.com/cgi-bin/login; ts_uid=3392060960",
        "referer": "https://y.qq.com/portal/singer_list.html"
    }
    paramter = {
        "g_tk": "5381",
        "callback": "getUCGI9688380858412697",
        "jsonpCallback": "getUCGI9688380858412697",
        "loginUin": "0",
        "hostUin": "0",
        "format": "jsonp",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": "0",
        "platform": "yqq",
        "needNewCode": "0",
        "data": '{"comm":{"ct":24,"cv":10000},"singerList":{"module":"Music.SingerListServer","method":"get_singer_list","param":{"area":%d,"sex":-100,"genre":-100,"index":-100,"sin":%d,"cur_page":%d}}}' % (area_id, (page_ind - 1) * 80, page_ind)
    }

    html_text = requests_dora.try_best_2_get(url=url, params=paramter, headers=header).text
    se = re.search("getUCGI9688380858412697\((.*)\)", html_text)
    json_str = None
    if se:
        json_str = se.group(1)

    data = json.loads(json_str)["singerList"]["data"]
    singerlist = data["singerlist"]
    try:
        area_ids = data["tags"]["area"]
    except Exception as e:
        area_ids = None
    singer_num_total = data["total"]
    return singerlist, singer_num_total, area_ids


def get_singer_list(area_id):
    singer_list_total = []
    singer_list, total, _ = get_singer_list_page(area_id, 1)
    singer_list_total.extend(singer_list)

    page_max = int(math.ceil(total / 80))
    for i in tqdm(range(1, page_max), desc = "getting singer list at area {}".format(area_id)):
        page_ind = i + 1
        singer_list, total, _ = get_singer_list_page(area_id, page_ind)
        singer_list_total.extend(singer_list)

    return singer_list_total


def crawl_song_list_page(singer_mid, begin):
    url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg"
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "cookie": "RK=7dNm4/X + Yj; tvfe_boss_uuid=bf00ee54e9081ab4; pgv_pvi=8772238336; pac_uid=1_857193777; pgv_pvid=6457341280; o_cookie=857193777; ptcz=c761e59c8c8d6bd5198866d02a5cb7313af1af468006c455d6c2b5d26201d42e; pgv_si=s10759168; _qpsvr_localtk=0.08285763449905015; ptisp=ctc; luin=o0857193777; lskey=00010000228dd1371b945c68ecfd3b71d3071425024a7a8a2a23e3ffcb5b9904c9f7088d2ea8c01539ffed92; pt2gguin=o0857193777; uin=o0857193777; skey=@Kydi7w0EI; p_uin=o0857193777; p_skey=HjsE9sEjznJfXk*9KFEeW4VZr6i3*tlXZ2nuzEw8kCg_; pt4_token=c-p6sv3JEboA51cSQ3ABqxM8O80Jct3jYYkgy-aEQuE_; p_luin=o0857193777; p_lskey=000400008f9c296cd10c03a5173d22a184aad124d791568e90e4198beb8ad699a4d02fbfc059f71ab3d8758c; ts_last=y.qq.com/portal/playlist.html; ts_refer=ui.ptlogin2.qq.com/cgi-bin/login; ts_uid=3392060960",
        "referer": "https://y.qq.com/n/yqq/singer/{}.html".format(singer_mid)
    }

    paramter = {
        "g_tk": "5381",
        "jsonpCallback": "MusicJsonCallbacksinger_track",
        "loginUin": "0",
        "hostUin": "0",
        "format": "jsonp",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": "0",
        "platform": "yqq",
        "needNewCode": "0",
        "singermid": singer_mid,
        "order": "listen",
        "begin": begin,
        "num": "30",
        "songstatus": "1",
    }

    html_text = requests_dora.try_best_2_get(url=url, params=paramter, headers=header).text
    json_str = html_text.lstrip(" MusicJsonCallbacksinger_track(").rstrip(")").strip()
    data = json.loads(json_str)["data"]
    song_list = data["list"]
    total_num = data["total"]
    song_list_new = []
    for song in song_list:
        song = song["musicData"]
        song_new = {}
        song_new["albumid"] = song["albumid"]
        song_new["albummid"] = song["albummid"]
        song_new["albumname"] = song["albumname"]
        song_new["songid"] = song["songid"]
        song_new["songmid"] = song["songmid"]
        song_new["songname"] = song["songname"]
        song_list_new.append(song_new)
    return song_list_new, int(total_num)


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


def crawl_song_list(singer, area):
    singer_mid = singer[KEY_SINGER_MID]
    singer_name = singer[KEY_SINGER_NAME]
    song_list_total = []
    song_list, total = crawl_song_list_page(singer_mid, 0)
    song_list_total.extend(song_list)

    p_ind_list = range(30, total, 30)
    for i in tqdm(p_ind_list, desc="getting song list of {}@{}...".format(singer_name, area)):
        song_list, total = crawl_song_list_page(singer_mid, i)
        song_list_total.extend(song_list)

    for song in tqdm(song_list_total, desc="getting the lyrics of the songs of {}@{}...".format(singer_name, area)):
        contributors, lyric = get_lyric(song)
        song[KEY_CONTRIBUTORS] = contributors
        song[KEY_LYRIC] = lyric
        song[KEY_SINGER_NAME] = singer_name

    return song_list_total


def crawl_songs(area_list, save_path):
    # get progress
    singer_id_done = []
    for root, dirs, files in os.walk(save_path):
        for file_name in files:
            singer_id = re.search("song_list_.*_(.*).json", file_name).group(1)
            singer_id_done.append(int(singer_id))

    _, _, area_ids = get_singer_list_page(-100, 1)
    area_2_id = {}
    for item in area_ids:
        area_2_id[item["name"]] = item["id"]

    for area in area_list:
        singer_list = get_singer_list(area_2_id[area])
        for singer in singer_list:
            singer_name = singer[KEY_SINGER_NAME]
            singer_id = singer[KEY_SINGER_ID]
            if singer_id in singer_id_done:
                continue
            song_list = crawl_song_list(singer, area)
            json.dump(song_list,
                      open("%s/song_list_%s_%s.json" % (save_path, singer_name, singer_id), "w", encoding="utf-8"), ensure_ascii = False)

if __name__ == "__main__":
    # # get singer list
    # singers = get_singer_list(-100)
    # print(len(singers))

    # crawl songs by areas
    area_list = ["港台", "内地"] # {'全部': -100, '内地': 200, '港台': 2, '欧美': 5, '日本': 4, '韩国': 3, '其他': 6}
    save_path = "./qq_music_songs_by_area"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    crawl_songs(area_list, save_path)

