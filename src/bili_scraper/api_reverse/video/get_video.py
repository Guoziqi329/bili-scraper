import os
import time
import requests
import json
import re
import tempfile
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import logging
from pathlib import Path

session = requests.Session()


def get_html(cookie: str, url: str) -> str:
    """
    get web page
    :param cookie: website's cookie information
    :param url: website's url
    :return: page html
    """
    headers = {
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    response = session.get(url, headers=headers)
    return response.text


def get_playinfo(html: str) -> dict:
    """
    get play information
    :param html: web page html
    :return: play information
    """
    info = re.findall('window.__playinfo__=(.*?)</script>', html)[0]
    info = json.loads(info)
    return info


def get_video_AND_audio_url(playinfo: dict, video_quality) -> tuple:
    """
    get video url and audio url
    :param playinfo: play information
    :param video_quality: video quality
    :return: video url and audio url
    """
    return playinfo['data']['dash']['video'][(video_quality - 1) * 3]['baseUrl'], playinfo['data']['dash']['audio'][0][
        'baseUrl']


def get_video(cookie: str, video_id: str, output_dir: str = None, select_video_quality: bool = False) -> None:
    """
    get video
    :param cookie: website's cookie information
    :type cookie: str
    :param video_id: the id in the url, such as BV1Mg8RzFExV
    :type video_id: str
    :param output_dir: the folder where the video will be saved
    :type output_dir: str
    :param select_video_quality: whether to choose video quality, default is not selected, video quality is the highest.
    :type select_video_quality: bool
    :return: None
    """
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    url = f'https://www.bilibili.com/video/{video_id}/'

    html = get_html(cookie, url)

    playinfo = get_playinfo(html)

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

    video_url, audio_url = get_video_AND_audio_url(playinfo, video_quality)

    headers = {
        'Referer': url,
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }

    video_content = requests.get(url=video_url, headers=headers).content
    audio_content = requests.get(url=audio_url, headers=headers).content

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

        final_clip.write_videofile(output_dir / 'output.mp4')
        time.sleep(1)

    finally:
        try:
            os.remove(video_path)
            os.remove(audio_path)
        except Exception:
            pass