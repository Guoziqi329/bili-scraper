from .article import get_article
from .video import get_video, get_video_dm, get_video_comments
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)

__all__ = ['get_article', 'get_video', 'get_video_dm', 'get_video_comments']
