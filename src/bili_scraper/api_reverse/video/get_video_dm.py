import json
import re
from .get_w_rid_And_wts import Get_w_rid_And_wts
from google.protobuf.json_format import MessageToJson

# dm_pb2 使用了 SocialSisterYi (https://github.com/SocialSisterYi) 的代码(https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/grpc_api/bilibili/community/service/dm/v1/dm.proto)
# 许可协议: CC-BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)
from . import dm_pb2


class GetDM:
    def __init__(self, session):
        self.session = session
        self.wridAndWts = Get_w_rid_And_wts(session)
        self.my_seg = dm_pb2.DmSegMobileReply()

    def get_html(self, url: str) -> str:
        """
        get web page
        :param url: website's url
        :return: page html
        """
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        response = self.session.get(url, headers=headers)
        return response.text

    @staticmethod
    def get__INITIAL_STATE__(html: str) -> dict:
        """
        get __INITIAL_STATE__
        :param html: web page html
        :return: web __INITIAL_STATE__
        """
        INITIAL_STATE = re.findall(r'window.__INITIAL_STATE__=(.*);\(function', html)[0]
        INITIAL_STATE = json.loads(INITIAL_STATE)
        return INITIAL_STATE

    @staticmethod
    def get_playinfo(html: str) -> dict:
        """
        get play information
        :param html: web page html
        :return: play information
        """
        info = re.findall('window\.__playinfo__=(.*?)</script>', html)[0]
        info = json.loads(info)
        return info

    def get_pid(self, video_id: str) -> str:
        """
        get video pid by video id
        :param video_id: the id in the url, such as BV1Mg8RzFExV
        :return: video's pid
        """
        url = f"https://www.bilibili.com/video/{video_id}/"

        html = self.get_html(url)

        INITIAL_STATE = self.get__INITIAL_STATE__(html)

        return str(INITIAL_STATE["aid"])

    def get_oid(self, video_id: str) -> str:
        """
        get video oid by video id
        :param video_id: the id in the url, such as BV1Mg8RzFExV
        :return: video's oid
        """
        url = f"https://www.bilibili.com/video/{video_id}/"

        html = self.get_html(url)

        playinfo = self.get_playinfo(html)

        return str(playinfo["data"]["last_play_cid"])

    def get_video_dm(self, video_id: str) -> list:
        """
        Get video dm
        :param video_id: the id in the url, such as BV1Mg8RzFExV
        :return: dm list
        """
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        }

        oid = self.get_oid(video_id)
        pid = self.get_pid(video_id)

        dm_list = list()

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

            w_rid, wts = self.wridAndWts.get_w_rid_And_wts(payload)

            payload["w_rid"] = w_rid
            payload["wts"] = wts

            response = self.session.get(url, headers=headers, params=payload)
            self.my_seg.ParseFromString(response.content)

            if len(self.my_seg.elems) == 0:
                break

            for item in json.loads(MessageToJson(self.my_seg))['elems']:
                dm_list.append({'id': item['id'] if 'id' in item.keys() else None,
                                'color': item['color'] if 'color' in item.keys() else None,
                                'ctime': item['ctime'] if 'ctime' in item.keys() else None,
                                'progress': item['progress'] if 'progress' in item.keys() else -1,
                                'content': item['content'] if 'content' in item.keys() else None})

            i = i + 1

        return dm_list
