import requests
import json
from datetime import datetime
from lxml import etree


def get_article_html(cookie: str, article_id: str):
    """
    get article html
    :param cookie: website's cookie information
    :param article_id: article's url such as 1097430290934005800 (https://www.bilibili.com/opus/1097430290934005800?spm_id_from=333.1387.0.0)
    :return: html
    """
    url = f"https://www.bilibili.com/opus/{article_id}"
    headers = {
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.text


def get_text(xpath_list):
    if len(xpath_list) == 0:
        return None
    else:
        return xpath_list[0].text


def get_article(cookie: str, article_id: str, storage_location: str = '.') -> None:
    """
    get_article
    :param cookie: website's cookie information.
    :param article_id: article's url such as 1097430290934005800 (https://www.bilibili.com/opus/1097430290934005800?spm_id_from=333.1387.0.0)
    :param storage_location: local storage in word.
    :return: None
    """
    html = get_article_html(cookie, article_id)
    element = etree.HTML(html)
    title = get_text(element.xpath('//*[@id="app"]/div[4]/div[1]/div[1]/span'))

    author_name = get_text(element.xpath('//*[@id="app"]/div[4]/div[1]/div[2]/div[2]/div[1]'))

    author_time = get_text(element.xpath('//*[@id="app"]/div[4]/div[1]/div[2]/div[2]/div[2]/div'))

    if author_time is not None:
        author_time = datetime.strptime(author_time, '编辑于 %Y年%m月%d日 %H:%M')

    content = element.xpath('//*[@id="app"]/div[4]/div[1]/div[4]/*')

    for item in content:
        print(item.tag)

    print(content)

    print(title, author_name, author_time)


if __name__ == '__main__':
    with open('../cookie.json', 'r') as f:
        cookie = json.load(f)['cookie']

    article_id = '1097430290934005800'
    get_article(cookie, article_id)
