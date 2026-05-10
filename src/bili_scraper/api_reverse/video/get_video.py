import os
import shutil
import json
import re
import tempfile
import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
from .get_w_rid_And_wts import Get_w_rid_And_wts
import logging
import imageio_ffmpeg
import subprocess
from pathlib import Path


class GetVideo:
    def __init__(self, session):
        self.session = session
        self.wridAndWts = Get_w_rid_And_wts(self.session)

    @staticmethod
    def get_ffmpeg_path():
        """获取 imageio-ffmpeg 自带的 ffmpeg 可执行文件路径"""
        return imageio_ffmpeg.get_ffmpeg_exe()

    @staticmethod
    def check_quick_splicing_video(video_path_list: list) -> bool:
        """
        check quick splicing video
        :param video_path_list: videos path
        :return: Is it possible to splicing quickly -> True or False
        """
        # get first video information
        first_video_path = video_path_list[0]
        cap = cv2.VideoCapture(first_video_path)
        if not cap.isOpened():
            raise IOError("Unable to open video file")

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        cap.release()

        for video_path in video_path_list[1:]:
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                raise IOError("Unable to open video file")

            if cap.get(cv2.CAP_PROP_FPS) != fps or int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) != width or int(
                    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) != height:
                return False

        return True

    def concatenate_videos_fast(self, video_path_list, output_path):
        ffmpeg_path = self.get_ffmpeg_path()

        # 创建 filelist.txt
        filelist_path = Path("filelist.txt")
        with open(filelist_path, "w", encoding="utf-8") as f:
            for path in video_path_list:
                # 使用绝对路径并转义单引号（如果路径中有）
                abs_path = Path(path).resolve().as_posix()
                f.write(f"file '{abs_path}'\n")

        try:
            cmd = [
                ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", str(filelist_path),
                "-c", "copy",
                "-y",
                str(output_path)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        finally:
            filelist_path.unlink(missing_ok=True)

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
    def get_playinfo(html: str) -> dict:
        """
        get play information
        :param html: web page html
        :return: play information
        """
        info = re.findall('window\.__playinfo__=(.*?)</script>', html)[0]
        info = json.loads(info)
        return info

    def get_initial_state(self, html: str) -> dict:
        """
        get initial state
        :param html: web page html
        :return: __INITIAL_STATE__
        """
        state = re.findall('window\.__INITIAL_STATE__=(.*?);', html)[0]
        state = json.loads(state)
        return state

    def get_video_AND_audio_url(self, playinfo: dict, video_quality) -> tuple:
        """
        get video url and audio url
        :param playinfo: play information
        :param video_quality: video quality
        :return: video url and audio url
        """
        return playinfo['data']['dash']['video'][(video_quality - 1) * 3]['baseUrl'], \
            playinfo['data']['dash']['audio'][0][
                'baseUrl']

    def get_video_info(self, playinfo: dict) -> tuple:
        """
        get video info
        :param playinfo: play information
        :return: video name, video desc, video pages
        """
        return playinfo['videoData']['title'], playinfo['videoData']['desc'], playinfo['videoData']['pages']

    def get_video(self, video_id: str, output_dir: str = None, select_video_quality: bool = False,
                  without_audio: bool = False, quick_splicing: bool = False, cache_dir: str = './cache/') -> None:
        """
        get video
        :param video_id: the id in the url, such as BV1Mg8RzFExV
        :type video_id: str
        :param output_dir: the folder where the video will be saved
        :type output_dir: str
        :param select_video_quality: whether to choose video quality, default is not selected, video quality is the highest.
        :type select_video_quality: bool
        :param without_audio: whether to remove audio, default is False.
        :type without_audio: bool
        :param quick_splicing: whether to use quick splicing, default is False.
        :type quick_splicing: bool
        :param cache_dir: cache folder
        :type cache_dir: str
        :return: None
        """
        if output_dir is None:
            output_dir = Path.cwd()
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        cache_dir = Path(cache_dir) / video_id
        cache_dir.mkdir(parents=True, exist_ok=True)

        video_name, video_desc, video_pages = self.get_video_info(
            self.get_initial_state(self.get_html(f'https://www.bilibili.com/video/{video_id}/')))

        video_path_list = list()

        for i in range(1, len(video_pages) + 1):
            if i == 1:
                url = f'https://www.bilibili.com/video/{video_id}/'
            else:
                url = f'https://www.bilibili.com/video/{video_id}/?p={i}'

            playinfo = self.get_playinfo(self.get_html(url))

            accept_description = playinfo['data']['accept_description']
            accept_quality = playinfo['data']['accept_quality']

            if select_video_quality:
                video_quality = -1
                while video_quality not in range(1, len(accept_quality) + 1):
                    print("please select video quality")
                    for i in range(1, len(accept_quality) + 1):
                        print(f'{i} : {accept_description[i - 1]}', end='\t')
                    video_quality = int(input('\n'))
                    if video_quality not in range(1, len(accept_quality) + 1):
                        logging.error('Parameter error, please select again.')
            else:
                video_quality = 1

            video_url, audio_url = self.get_video_AND_audio_url(playinfo, video_quality)

            headers = {
                'Referer': url,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
            }

            video_content = self.session.get(url=video_url, headers=headers).content

            if without_audio:
                with open(tmp := cache_dir / f'{video_name}_{i}.mp4', 'wb') as f:
                    f.write(video_content)
                    video_path_list.append(tmp)
                continue

            audio_content = self.session.get(url=audio_url, headers=headers).content

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
                tmp_video.write(video_content)
                video_path = tmp_video.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                tmp_audio.write(audio_content)
                audio_path = tmp_audio.name

            try:
                video_clip = VideoFileClip(video_path)
                audio_clip = AudioFileClip(audio_path)

                final_clip = video_clip.with_audio(audio_clip)

                final_clip.write_videofile(tmp := cache_dir / f'{video_name}_{i}.mp4')
                video_path_list.append(tmp)

            finally:
                try:
                    os.remove(video_path)
                    os.remove(audio_path)
                except Exception:
                    pass

        if len(video_path_list) >= 2:
            if quick_splicing and self.check_quick_splicing_video(video_path_list):
                self.concatenate_videos_fast(video_path_list, output_dir / f"{video_name}_clip.mp4")
            else:
                clip_list = [VideoFileClip(clip_list) for clip_list in video_path_list]
                final_clip = concatenate_videoclips(clip_list)
                final_clip.write_videofile(output_dir / f"{video_name}_clip.mp4")
        else:
            shutil.move(video_path_list[0], output_dir / f'{video_name}.mp4')

        # delete videos
        for video_path in video_path_list:
            os.remove(video_path)
