from .article import get_article
from .video import GetVideo, GetDM, GetComments
from .login import Login
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)

__all__ = ['get_article', 'GetVideo', 'GetDM', 'GetComments', 'Login']
