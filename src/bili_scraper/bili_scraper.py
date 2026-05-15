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
        """
        get session cookie
        :return: session.cookies
        """
        return self.session.cookies

    def getArticle(self, article_id, doc_storage_location=None, document_name='Document.doc', img_path=None) -> str:
        """
        get article from bilibili
        :param article_id: article id
        :param doc_storage_location: document storage location, default None
        :param document_name: document name, default 'Document.doc'
        :param img_path: image path, default None
        :return: document text
        """
        return self.GetArticle.get_article(article_id, doc_storage_location, document_name, img_path)

    def getVideo(self, video_id, output_dir=None, select_video_quality=False, without_audio: bool = False,
                 quick_splicing: bool = False, cache_dir: str = './cache/') -> None:
        """
        get video from bilibili
        :param video_id: the id in the url, such as BV1Mg8RzFExV
        :param output_dir: the folder where the video will be saved
        :param select_video_quality: whether to choose video quality, default is not selected, video quality is the highest.
        :param without_audio: whether to remove audio, default is False.
        :param quick_splicing: whether to use quick splicing, default is False.
        :param cache_dir: cache folder
        :return: None
        """
        self.GetVideo.get_video(video_id, output_dir, select_video_quality, without_audio, quick_splicing, cache_dir)

    def getVideoDm(self, video_id) -> list:
        """
        get video's DM from bilibili
        :param video_id: the id in the url, such as BV1Mg8RzFExV
        :return: dm list
        """
        return self.GetDM.get_video_dm(video_id)

    def getVideoComments(self, video_id, img_path=None, delay=3) -> list:
        """
        get video's comments from bilibili
        :param video_id: the id in the url, such as BV1Mg8RzFExV
        :param img_path: directory of images
        :param delay: interval time for initiating requests, the default value is 3.
        :return: comments list
        """
        return self.GetComments.get_video_comments(video_id, img_path, delay)

    def get_loginer(self):
        """
        get loginer
        :return: self.loginer
        """
        return self.loginer

    def __update(self):
        self.GetVideo = GetVideo(self.session)
        self.GetDM = GetDM(self.session)
        self.GetComments = GetComments(self.session)
        self.GetArticle = GetArticle(self.session)

    def set_cookies(self, cookies) -> None:
        """
        set cookies
        :param cookies: cookies
        :return: None
        """
        self.session.cookies.update(cookies)
        self.loginer = Login(self.session)
        self.__update()

    def Login(self) -> None:
        """
        login with scanning QRCode
        :return: None
        """
        self.loginer.LoginWithQRCode()
        self.__update()

    def check_session(self) -> bool:
        """
        Check session validity
        :return: True or False
        """
        return self.loginer.check_session()

    def get_login_url_And_qrcode_key(self) -> tuple:
        """
        get login url and qrcode key
        :return: login_url, qrcode_key
        """
        return self.loginer.get_login_url_AND_qrcode_key()

    def checkQRCode(self, qrcode_key) -> int:
        """
        Check QR code validity
        :param qrcode_key: qrcode key
        :return: code
        """
        return self.loginer.checkQRCode(qrcode_key)

    def get_user_info(self) -> dict:
        """
        get user info
        :return: user info
        """
        return self.loginer.get_user_info()