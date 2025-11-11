import os
import requests
import json
import time
import re
from pathlib import Path
from .get_w_rid_And_wts import get_wbiImgKey_and_wbiSubKey, get_w_rid_And_wts, encodeURIComponent

session = requests.Session()


def get_oid(cookie: str, video_id: str) -> str:
    """
    get video oid by video id
    :param cookie: website's cookie information
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
                at_information = {"at_name": list(item['content']['at_name_to_mid_str'].keys())[0],
                                  "pid": list(item['content']['at_name_to_mid_str'].values())[0]}
            else:
                at_information = None

            jump_url_list = list()
            if len(item['content']['jump_url'].keys()) > 0:
                for jump_url in item['content']['jump_url'].keys():
                    jump_url_list.append(jump_url if '/' in jump_url else f'https://b23.tv/{jump_url}')
            else:
                jump_url_list = None

            comments.append({"rpid": item['rpid_str'],
                             "message": item['content']['message'],
                             "at_information": at_information,
                             "jump_url": jump_url_list})
        time.sleep(delay)

    print(comments)
    return comments


def create_path(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def get_img(url: str, img_dir: Path, name: str) -> Path:
    """
    get img from url
    :param url: img url
    :param img_dir: directory of images
    :param name: img name
    :return: img path
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    response = session.get(url, headers=headers)

    img_dir.mkdir(parents=True, exist_ok=True)

    with open(img_dir/f'{name}.{url.split('.')[-1]}', 'wb') as f:
        f.write(response.content)
    return Path.cwd()/img_dir/f'{name}.{url.split('.')[-1]}'


def process_response(cookie, response, comments: list, oid: str, video_id: str, img_dir: str = None, delay: int = 3) -> list:
    """
    Response handling
    :param cookie: website's cookie information
    :param response: response from bilibili
    :param comments: comments list
    :param oid: video id
    :param video_id: the id in the url, such as BV1Mg8RzFExV
    :param img_dir: directory of images
    :param delay: Interval time for initiating requests, the default value is 3.
    :return: comments list
    """
    if img_dir is None:
        img_dir = Path.cwd()
    else:
        img_dir = Path(img_dir)

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
                                 "img_path": str(get_img(pic['img_src'], img_dir / video_id / item["rpid_str"], str(i)))})
                i += 1
                time.sleep(delay)
        else:
            img_list = None

        jump_url_list = list()
        if len(item['content']['jump_url'].keys()) > 0:
            for jump_url in item['content']['jump_url'].keys():
                jump_url_list.append(jump_url if '/' in jump_url else f'https://b23.tv/{jump_url}')
        else:
            jump_url_list = None

        comments.append({'rpid': item['rpid_str'], 'message': item['content']['message'],
                         'reply': second_level_comments, 'img': img_list, 'jump_url': jump_url_list})

        print(item['content']['message'])

    print('-' * 200)
    return comments


def get_video_comments(cookie: str, video_id: str, img_path: str = None, delay: int = 3) -> list:
    """
    get video comments
    :param cookie: website's cookie information
    :param video_id: the id in the url, such as BV1Mg8RzFExV
    :param img_path: directory of images
    :param delay: Interval time for initiating requests, the default value is 3.
    :return: comment information
    """

    comments = list()

    oid = get_oid(cookie, video_id)

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

    comments = process_response(cookie, response, comments, oid, video_id, img_path, delay)

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

        comments = process_response(cookie, response, comments, oid, video_id, img_path, delay)

        time.sleep(delay)

    return comments


if __name__ == '__main__':
    with open('../cookie.json', 'r') as f:
        cookie = json.load(f)['cookie']

    video_id = 'BV1xqgazCECb'
    comments = get_video_comments(cookie, video_id, '../img')

    with open(f"result.json", "w", encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False)
