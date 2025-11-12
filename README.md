
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

You can install it using the 'pip install bili-scraper' command

### Demo

``` python
from bili_scraper import BiliScraper
import json

if __name__ == '__main__':
    with open("cookie.json", "r", encoding="utf-8") as f:
        cookie = json.load(f)['cookie']

    bilibili = BiliScraper(cookie)

    # Get video
    bilibili.getVideo('BV1Jd1oB3EGD')

    # Get video comments
    comments = bilibili.getVideoComments('BV1Jd1oB3EGD', 'img', 1)
    with open("test.json", "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False)
    
    # Get video Dm
    print(bilibili.getVideoDm("BV1vxPReEERx"))

    # Get Article
    bilibili.getArticle("1102463389176692741", 'doc', 'doc.docx', 'img/test/')
```



## Thanks
This project uses code from:
- [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) by [@SocialSisterYi], licensed under [CC-BY-NC 4.0](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/LICENSE)


## feedback

If you have any feedback, please contact us：guoziqi329@gmail.com

