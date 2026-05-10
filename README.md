
# bili-scraper

Bilibili website crawler that can download videos, dm, comments, articles, and more.

This project is for learning purposes only, **please don’t use it for commercial purposes**.

本项目仅用于学习目的，**请勿用于商业用途**。

## License

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/Guoziqi329/bili-scraper/blob/main/LICENSE)



## Author

- [@Guoziqi329](https://github.com/Guoziqi329)
- [@su7-ran](https://github.com/su7-ran)

## start

You can install it using the ```pip install bili-scraper``` command

### Demo

``` python
from bili_scraper import BiliScraper
import json

if __name__ == '__main__':
    bilibili = BiliScraper()
    # with open('cookie.json', 'r') as f:
    #     cookie = json.load(f)
    # bilibili.set_cookies(cookie)
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
```



## Thanks
This project uses code from:
- [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) by [@SocialSisterYi], licensed under [CC-BY-NC 4.0](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/LICENSE)


## feedback

If you have any feedback, please contact us：guoziqi329@gmail.com

