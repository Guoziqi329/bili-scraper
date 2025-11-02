from api_reverse.article import get_article
from api_reverse.video import get_video ,get_video_dm, get_video_comments


class BilibiliCrawler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, cookie):
        self.cookie = cookie

    def getArticle(self, article_id, doc_storage_location = '.', document_name = 'Document.doc', img_path = 'img'):
        get_article(self.cookie, article_id, doc_storage_location, document_name, img_path)

    def getVideo(self, video_id, path = '.', select_video_quality = False):
        get_video(self.cookie, video_id, path, select_video_quality)

    def getVideoDm(self, video_id):
        get_video_dm(self.cookie, video_id)

    def getVideoComments(self, video_id, img_path = '.', delay = 3):
        get_video_comments(self.cookie, video_id, img_path, delay)


