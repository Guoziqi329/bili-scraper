import requests
import json
import time
from get_w_rid_And_wts import get_wbiImgKey_and_wbiSubKey, get_w_rid_And_wts, encodeURIComponent

session = requests.Session()


def get_offset(response) -> str:
    return response.json()['data']['cursor']['pagination_reply']['next_offset']


if __name__ == '__main__':
    with open('cookie.json', 'r') as f:
        config = json.load(f)
    cookie = config['cookie']
    payload = {
        "oid": "814225886",
        "type": "1",
        "mode": "3",
        "pagination_str": "{\"offset\":\"\"}",
        "plat": "1",
        "seek_rpid": None,
        "web_location": "1315875"
    }


    wbiImgKey, wbiSubKey = get_wbiImgKey_and_wbiSubKey(cookie)
    w_rid, wts = get_w_rid_And_wts(wbiImgKey, wbiSubKey, payload)
    print(w_rid, wts)
    payload["w_rid"] = w_rid
    payload["wts"] = wts

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "cookie": cookie,
    }

    response = session.get("https://api.bilibili.com/x/v2/reply/wbi/main", headers=headers, params=payload)
    next_offset = get_offset(response)
    # print(response.json())
    with open("test.json", "w", encoding='utf-8') as f:
        json.dump(response.json(), f)

    for item in response.json()['data']['replies']:
        print(item['rpid'])
        print('*'*50)

    print('-' * 100)

    time.sleep(1)

    for i in range(5):

        payload_2 = {
            "oid": "814225886",
            "type": "1",
            "mode": "3",
            "pagination_str": "{\"offset\":\"" + next_offset + "\"}",
            "plat": "1",
            "web_location": "1315875"
        }

        wbiImgKey, wbiSubKey = get_wbiImgKey_and_wbiSubKey(cookie)
        w_rid, wts = get_w_rid_And_wts(wbiImgKey, wbiSubKey, payload_2)
        print(w_rid, wts)
        payload_2["w_rid"] = w_rid
        payload_2["wts"] = wts
        response = session.get("https://api.bilibili.com/x/v2/reply/wbi/main", headers=headers, params=payload_2)
        # print(response.json())
        with open(f"test{i}.json", "w", encoding='utf-8') as f:
            json.dump(response.json(), f)

        for item in response.json()['data']['replies']:
            print(item['rpid'])
            print('*'*50)

        print('-'*200)

        next_offset = get_offset(response)

        time.sleep(5)
