from .api_reverse.article import GetArticle
from .api_reverse.video import GetVideo, GetDM, GetComments
from .api_reverse.login import Login
import requests


class BiliScraper:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.session = requests.Session()
        self.loginer = Login(self.session)
        self.__update()

    def getCookie(self):
        return self.session.cookies

    def getArticle(self, article_id, doc_storage_location=None, document_name='Document.doc', img_path=None):
        return self.GetArticle.get_article(article_id, doc_storage_location, document_name, img_path)

    def getVideo(self, video_id, output_dir=None, select_video_quality=False, without_audio: bool = False,
                 quick_splicing: bool = False, cache_dir: str = './cache/'):
        self.GetVideo.get_video(video_id, output_dir, select_video_quality, without_audio, quick_splicing, cache_dir)

    def getVideoDm(self, video_id):
        return self.GetDM.get_video_dm(video_id)

    def getVideoComments(self, video_id, img_path=None, delay=3):
        return self.GetComments.get_video_comments(video_id, img_path, delay)

    def get_loginer(self):
        return self.loginer

    def __update(self):
        self.GetVideo = GetVideo(self.session)
        self.GetDM = GetDM(self.session)
        self.GetComments = GetComments(self.session)
        self.GetArticle = GetArticle(self.session)

    def set_cookies(self, cookies):
        self.session.cookies.update(cookies)
        self.loginer = Login(self.session)
        self.__update()


    def Login(self):
        self.loginer.LoginWithQRCode()
        self.__update()

    def check_session(self):
        return self.loginer.check_session()
