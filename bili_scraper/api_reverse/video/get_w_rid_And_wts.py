import requests
import time
import urllib.parse
import json
from hashlib import md5


def get_wbiImgKey_and_wbiSubKey(cookie: str):
    """
    get wbiImgKey and wbiSubKey
    :param cookie: website's cookie information
    :return: wbiImgKey, wbiSubKey
    """
    url = 'https://api.bilibili.com/x/web-interface/nav'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'cookie': cookie
    }
    response = requests.get(url, headers=headers)
    wbi_img = response.json()["data"]["wbi_img"]
    return wbi_img["img_url"].split('/')[-1].split('.')[0], wbi_img["sub_url"].split('/')[-1].split('.')[0]


def encodeURIComponent(s: str) -> str:
    """
    encode url component
    :param s: str
    :return: str
    """
    return urllib.parse.quote(s, safe='')


def get_w_rid_And_wts(wbiImgKey: str, wbiSubKey: str, e: dict):
    """
    get w_rid and wts
    :param wbiImgKey: wbiImgKey
    :param wbiSubKey: wbiSubKey
    :param e: requests payload, each key must be a string and each value must be a string or None
    :return: w_rid, wts
    """
    t = wbiImgKey + wbiSubKey
    r = list()
    MIXIN_KEY_ENC_TAB = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29,
                         28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25,
                         54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52]
    for i in MIXIN_KEY_ENC_TAB:
        if i < len(t):
            r.append(t[i])
    a = ''.join(r)[0:32]

    u = round(time.time())
    e["wts"] = str(u)

    c = sorted(e.keys())
    l = list()
    for key in c:
        value = e[key]
        if value is not None and type(value) == str:
            for old in ["!", "'", "(", ")", "*"]:
                value = value.replace(old, '')
            l.append(encodeURIComponent(key) + "=" + encodeURIComponent(value))
    v = "&".join(l)
    return md5((v + a).encode()).hexdigest(), str(u)


if __name__ == '__main__':
    with open("../../../cookie.json", 'r') as f:
        cookie = json.load(f)["cookie"]

    wbiImgKey, wbiSubKey = get_wbiImgKey_and_wbiSubKey(cookie)

    e = {"cm_from_track_id": None,
         "mode": "3",
         "oid": "814225886",
         "pagination_str": "{\"offset\":\"CAESEDE3OTU4OTI0MzE0NTIzNjIiAggB\"}",
         "plat": "1",
         "seek_rpid": None,
         "type": "1",
         "web_location": "1315875"}
    w_rid, wts = get_w_rid_And_wts(wbiImgKey, wbiSubKey, e)
    print(w_rid, wts)
