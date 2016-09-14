# coding=utf-8
import re
import webbrowser

import requests
from bs4 import BeautifulSoup, Comment
from flask import Flask, request, Response
from future.backports.html.parser import HTMLParser

app = Flask(__name__)

HOST = 'http://habrahabr.ru'


def process_content(content):
    content = content.replace('http://habrahabr.ru/', '/'). \
        replace('https://habrahabr.ru/', '/')
    soup = BeautifulSoup(content, 'html.parser')

    pattern = re.compile(ur'(\b[^ \&;:\.-]{6}\b)', re.UNICODE)
    html_parser = HTMLParser()

    elements_list = soup.find('body').find_all(text=True)

    for element in elements_list:
        parent = next(element.parents, None)
        if isinstance(element, Comment) or \
                (parent and parent.name in ['script', 'style']):
            continue

        text_value = element.string
        if text_value:
            text_value = html_parser.unescape(text_value)
            element.string.replaceWith(pattern.sub(ur'\1™', text_value))

    return soup.prettify(formatter="html")


@app.route('/', methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def other(path=''):
    headers = {
        key: value
        for key, value in request.headers.environ.iteritems()
        if value and isinstance(value, str)
        }
    response = requests.get(HOST + request.path, headers=headers)

    if 'html' in response.headers.get('content-type') and response.content:
        return process_content(response.content)
    else:
        return Response(response=response,
                        status=response.status_code,
                        headers=dict(response.headers),
                        content_type=response.headers.get('content-type'))


if __name__ == '__main__':
    webbrowser.open('http://0.0.0.0:8000', new=1)
    app.run(host='0.0.0.0', port=8000)
