import requests
import json
import re
from get_w_rid_And_wts import get_w_rid_And_wts, get_wbiImgKey_and_wbiSubKey
from google.protobuf.json_format import MessageToJson

# dm_pb2 使用了 SocialSisterYi (https://github.com/SocialSisterYi) 的代码(https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/grpc_api/bilibili/community/service/dm/v1/dm.proto)
# 许可协议: CC-BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)
import dm_pb2
from get_video import get_playinfo, get_html

session = requests.Session()

my_seg = dm_pb2.DmSegMobileReply()


def get__INITIAL_STATE__(html: str) -> dict:
    """
    get __INITIAL_STATE__
    :param html: web page html
    :return: web __INITIAL_STATE__
    """
    INITIAL_STATE = re.findall(r'window.__INITIAL_STATE__=(.*);\(function', html)[0]
    INITIAL_STATE = json.loads(INITIAL_STATE)
    return INITIAL_STATE


def get_pid(cookie: str, video_id: str) -> str:
    """
    get video pid by video id
    :param cookie: website's cookie information
    :param video_id: the id in the url, such as BV1Mg8RzFExV
    :return: video's pid
    """
    url = f"https://www.bilibili.com/video/{video_id}/"

    html = get_html(cookie, url)

    INITIAL_STATE = get__INITIAL_STATE__(html)

    return str(INITIAL_STATE["aid"])


def get_oid(cookie: str, video_id: str) -> str:
    """
    get video oid by video id
    :param cookie: website's cookie information
    :param video_id: the id in the url, such as BV1Mg8RzFExV
    :return: video's oid
    """
    url = f"https://www.bilibili.com/video/{video_id}/"

    html = get_html(cookie, url)

    playinfo = get_playinfo(html)

    return str(playinfo["data"]["last_play_cid"])


def get_video_dm(cookie: str, video_id: str) -> list:
    """
    Get video dm
    :param cookie: website's cookie information
    :param video_id: the id in the url, such as BV1Mg8RzFExV
    :return: dm list
    """
    headers = {
        "cookie": cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    }

    oid = get_oid(cookie, video_id)
    pid = get_pid(cookie, video_id)

    dm_list = list()

    print(len(my_seg.elems))

    i = 0

    ps = [0, 120000]
    pe = [120000, 360000]

    url = 'https://api.bilibili.com/x/v2/dm/wbi/web/seg.so'

    while True:
        if i < 2:
            payload = {
                "type": "1",
                "oid": oid,
                "pid": pid,
                "segment_index": "1",
                "pull_mode": "1",
                "ps": ps[i],
                "pe": pe[i],
                "web_location": "1315873"
            }
        else:
            payload = {
                "type": "1",
                "oid": oid,
                "pid": pid,
                "segment_index": str(i),
                "web_location": "1315873"
            }

        wbiImgKey, wbiSubKey = get_wbiImgKey_and_wbiSubKey(cookie)

        w_rid, wts = get_w_rid_And_wts(wbiImgKey, wbiSubKey, payload)

        payload["w_rid"] = w_rid
        payload["wts"] = wts

        response = session.get(url, headers=headers, params=payload)
        my_seg.ParseFromString(response.content)

        if len(my_seg.elems) == 0:
            break

        for item in json.loads(MessageToJson(my_seg))['elems']:
            dm_list.append({'id': item['id'] if 'id' in item.keys() else None,
                            'color': item['color'] if 'color' in item.keys() else None,
                            'ctime': item['ctime'] if 'ctime' in item.keys() else None,
                            'progress': item['progress'] if 'progress' in item.keys() else -1,
                            'content': item['content'] if 'content' in item.keys() else None})

        i = i + 1

    return dm_list


if __name__ == '__main__':
    with open("../cookie.json", 'r') as f:
        cookie = json.load(f)["cookie"]

    video_id = 'BV1MU4y137Yi'
    dm = get_video_dm(cookie, video_id)

    dm = sorted(dm, key=lambda x: x['progress'])

    with open('dm.json', 'w', encoding='utf-8') as f:
        json.dump(dm, f, ensure_ascii=False)
