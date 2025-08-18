import time
import requests
import json
import re
import os
from datetime import datetime
from lxml import etree
from docx import Document
from docx.shared import RGBColor, Pt, Cm
from docx.oxml.ns import qn


def create_path(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


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


def get_p_tag_text(html) -> str:
    result = html.xpath('./span | ./strong')
    if len(result) != 0:
        return ''.join(result[i].text for i in range(0, len(result)))
    else:
        return '\n'


def get_div_tag_img(cookie, item, path) -> list:
    html_list = item.xpath('.//img')

    result = list()
    for html in html_list:
        if not html.attrib['src']:
            continue
        url = 'https:' + html.attrib['src']
        if "@" in url:
            url = re.findall(r'(.*)@.*', url)[0]

        headers = {
            'cookie': cookie,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        time.sleep(0.5)

        create_path(path)

        name = url.split('/')[-1]

        with open(f'{path}/{name}', 'wb') as f:
            f.write(response.content)

        print(f'{path}/{name}')
        result.append(f'{path}/{name}')

    return result


def add_text(doc, text):
    paragraph = doc.add_paragraph(text)

    for run in paragraph.runs:
        run.font.color.rgb = RGBColor(47, 50, 56)
        run.font.size = Pt(17 / 1.5)
        run.font.name = "黑体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')


def add_image(doc, image_path_list):
    section = doc.sections[0]

    available_width = (section.page_width - section.left_margin - section.right_margin)

    for image_path in image_path_list:
        doc.add_picture(image_path, width=available_width)


def get_article(cookie: str, article_id: str, doc_storage_location: str = '.', document_name: str = 'Document.doc',img_path: str = 'img') -> None:
    """
    get_article
    :param cookie: website's cookie information.
    :param article_id: article's url such as 1097430290934005800 (https://www.bilibili.com/opus/1097430290934005800?spm_id_from=333.1387.0.0)
    :param doc_storage_location: doc local storage in word.
    :param img_path: img path
    :return: None
    """
    html = get_article_html(cookie, article_id)
    element = etree.HTML(html)
    title = get_text(element.xpath('//span[@class="opus-module-title__text"]'))

    doc = Document()

    section = doc.sections[0]
    section.page_width = Cm(21)  # 宽度 21 厘米
    section.page_height = Cm(29.7)

    author_name = get_text(element.xpath('//div[@class="opus-module-author__name"]'))
    author_time = get_text(element.xpath('//div[@class="opus-module-author__pub__text"]'))

    if author_time is not None:
        if '编辑于' in author_time:
            author_time = datetime.strptime(author_time, '编辑于 %Y年%m月%d日 %H:%M')
        else:
            author_time = datetime.strptime(author_time, '%Y年%m月%d日 %H:%M')

    if title is not None:
        doc_title = doc.add_heading(title, level=1)
        for run in doc_title.runs:
            run.font.color.rgb = RGBColor(0, 0, 0)
            run.font.size = Pt(22 / 1.5)

    doc_name = doc.add_paragraph(author_name)
    doc_time = doc.add_paragraph(author_time.strftime("%Y/%m/%d %H:%M"))

    for run in doc_name.runs:
        run.font.color.rgb = RGBColor(0, 0, 0)
        run.font.size = Pt(17 / 1.5)
        run.font.name = "黑体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

    for run in doc_time.runs:
        run.font.color.rgb = RGBColor(148, 153, 160)
        run.font.size = Pt(13 / 1.5)

    content = element.xpath('//div[@class="opus-module-content"]/*')

    for item in content:
        print(item.tag)
        if item.tag == 'p':
            print(get_p_tag_text(item))
            add_text(doc, get_p_tag_text(item))
        elif item.tag == 'div':
            add_image(doc, get_div_tag_img(cookie, item, img_path))

    print(content)

    print(title, author_name, author_time)

    doc.save(f'{doc_storage_location}/{document_name}')


if __name__ == '__main__':
    with open('../cookie.json', 'r') as f:
        cookie = json.load(f)['cookie']

    article_id = '1097430290934005800'
    get_article(cookie, article_id)
