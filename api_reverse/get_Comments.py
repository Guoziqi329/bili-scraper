import os
import requests
import json
import time
import re
from get_w_rid_And_wts import get_wbiImgKey_and_wbiSubKey, get_w_rid_And_wts, encodeURIComponent

session = requests.Session()


def get_oid(video_id: str, cookie) -> str:
    """
    get video oid by video id
    :param video_id: the id in the url, such as BV1Mg8RzFExV
    :return: video's oid
    """
    url = f"https://www.bilibili.com/video/{video_id}/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "cookie": cookie,
    }
    response = session.get(url, headers=headers)
    return re.search(r'"aid":\d+', response.text)[0][6:]


def get_offset(response) -> str:
    """
    get next offset
    :param response: requests response
    :return: next offset (str)
    """
    return response.json()['data']['cursor']['pagination_reply']['next_offset']


def get_comments_on_the_comment(cookie: str, oid: str, root: str, pages: int, delay: int = 3) -> list:
    """
    get comments on a comment
    :param cookie: website's cookie information
    :param oid: video id
    :param root: the rpid_str of the upper level comment
    :param pages: the number of pages in the reply
    :param delay: Interval time for initiating requests, the default value is 3.
    :return: second-level comment information
    """
    url = 'https://api.bilibili.com/x/v2/reply/reply'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "cookie": cookie,
    }

    comments = list()

    for i in range(1, pages + 1):
        payload = {
            "oid": oid,
            "type": "1",
            "root": root,
            "ps": "10",
            "pn": str(i),
            "web_location": "333.788"
        }
        response = session.get(url, headers=headers, params=payload)
        for item in response.json()['data']['replies']:
            if "at_name_to_mid_str" in item['content'].keys():
                have_at = True
                at_information = {"at_name": list(item['content']['at_name_to_mid_str'].keys())[0],
                                  "pid": list(item['content']['at_name_to_mid_str'].values())[0]}
            else:
                have_at = False
                at_information = None
            comments.append({"rpid": item['rpid_str'],
                             "message": item['content']['message'],
                             "have_at": have_at,
                             "at_information": at_information})
        time.sleep(delay)

    print(comments)
    return comments


def create_path(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def get_img(url: str, path: str, name: str) -> str:
    """
    get img from url
    :param url: img url
    :param path: directory of images
    :param name: img name
    :return: img path
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    response = session.get(url, headers=headers)
    create_path(f'{path}')
    path = path.strip('/')
    with open(f'{path}/{name}.{url.split('.')[-1]}', 'wb') as f:
        f.write(response.content)
    return f'{path}/{name}.{url.split('.')[-1]}'


def process_response(response, comments: list, oid: str, delay: int = 3) -> list:
    """
    process response
    :param response: response from bilibili
    :param comments: comments list
    :param oid: video id
    :param delay: Interval time for initiating requests, the default value is 3.
    :return: comments list
    """
    for item in response.json()['data']['replies']:
        if item['rcount'] > 0:
            second_level_comments = get_comments_on_the_comment(cookie, oid, item['rpid_str'],
                                                                int(item['rcount'] / 10) + 1
                                                                if item['rcount'] % 10 != 0
                                                                else int(item['rcount'] / 10), delay)
        else:
            second_level_comments = None

        img_list = list()

        i = 1
        if 'pictures' in item['content'].keys():
            for pic in item['content']['pictures']:
                img_list.append({"img_src": pic["img_src"],
                                 "img_path": get_img(pic['img_src'], f'./img/{item['rpid_str']}', str(i))})
                i += 1
                time.sleep(delay)
        else:
            img_list = None

        comments.append({'rpid': item['rpid_str'], 'message': item['content']['message'],
                         'reply': second_level_comments, 'img': img_list})

        print(item['content']['message'])
        print('*' * 50)

    print('-' * 200)
    return comments


def get_video_comments(cookie: str, video_id: str, delay: int = 3) -> list:
    """
    get video comments
    :param cookie: website's cookie information
    :param video_id: the id in the url, such as BV1Mg8RzFExV
    :param delay: Interval time for initiating requests, the default value is 3.
    :return: comment information
    """

    comments = list()

    oid = get_oid(video_id, cookie)

    payload = {
        "oid": oid,
        "type": "1",
        "mode": "3",
        "pagination_str": "{\"offset\":\"\"}",
        "plat": "1",
        "seek_rpid": None,
        "web_location": "1315875"
    }

    wbiImgKey, wbiSubKey = get_wbiImgKey_and_wbiSubKey(cookie)
    w_rid, wts = get_w_rid_And_wts(wbiImgKey, wbiSubKey, payload)
    payload["w_rid"] = w_rid
    payload["wts"] = wts

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "cookie": cookie,
    }

    response = session.get("https://api.bilibili.com/x/v2/reply/wbi/main", headers=headers, params=payload)

    process_response(response, comments, oid, delay)

    time.sleep(delay)

    while response.json()['data']['cursor']['pagination_reply'] is not None:
        next_offset = get_offset(response)
        payload_2 = {
            "oid": oid,
            "type": "1",
            "mode": "3",
            "pagination_str": "{\"offset\":\"" + next_offset + "\"}",
            "plat": "1",
            "web_location": "1315875"
        }

        wbiImgKey, wbiSubKey = get_wbiImgKey_and_wbiSubKey(cookie)
        w_rid, wts = get_w_rid_And_wts(wbiImgKey, wbiSubKey, payload_2)
        payload_2["w_rid"] = w_rid
        payload_2["wts"] = wts
        response = session.get("https://api.bilibili.com/x/v2/reply/wbi/main", headers=headers, params=payload_2)

        # Crawling finished, exit the loop.
        if len(response.json()['data']['replies']) == 0:
            break

        process_response(response, comments, oid, delay)

        time.sleep(delay)

    with open("result.json", "w", encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False)
    return comments


if __name__ == '__main__':
    with open('cookie.json', 'r') as f:
        cookie = json.load(f)['cookie']

    video_id = 'BV1Mg8RzFExV'
    get_video_comments(cookie, video_id)
