from BilibiliCrawling import BilibiliCrawler
import json

if __name__ == '__main__':
    with open("api_reverse/cookie.json", "r", encoding="utf-8") as f:
        cookie = json.load(f)['cookie']

    bilibili = BilibiliCrawler(cookie)

    bilibili.getVideo('BV1Jd1oB3EGD','video/video')

    comments = bilibili.getVideoComments('BV1Jd1oB3EGD', 'img', 1)

    with open("test.json", "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False)

    print(bilibili.getVideoDm("BV1vxPReEERx"))

    bilibili.getArticle("1102463389176692741", 'doc', 'doc.docx', 'img/test/')