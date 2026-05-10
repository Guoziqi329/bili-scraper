from src.bili_scraper.bili_scraper import BiliScraper
import json

if __name__ == '__main__':
    bilibili = BiliScraper()
    with open('cookie.json', 'r') as f:
        cookie = json.load(f)
    bilibili.set_cookies(cookie)
    bilibili.Login()

    with open('cookie.json', 'w') as f:
        json.dump(dict(bilibili.getCookie()), f)

    bilibili.getVideo('BV15bdmBNEZr', output_dir='./video', quick_splicing=True)

    comments = bilibili.getVideoComments('BV15bdmBNEZr', './img', 1)

    with open("comments.json", "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False)

    dm = bilibili.getVideoDm("BV15bdmBNEZr")
    with open('dm.json', 'w', encoding='utf-8') as f:
        json.dump(dm, f, ensure_ascii=False)

    bilibili.getArticle("1199888451663560745", 'doc', 'doc.docx', './article/img/')