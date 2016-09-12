# coding=utf-8
import re

import requests
from flask import Flask, request, Response
from lxml import html
from lxml.html import soupparser

app = Flask(__name__)

HOST = 'http://habrahabr.ru'


def process_content(content):
    content = content.replace('http://habrahabr.ru/', '/').replace('https://habrahabr.ru/', '/')

    doc = html.fromstring(content)
    try:
        ignore = html.tostring(doc, encoding=unicode)
    except UnicodeDecodeError:
        doc = soupparser.fromstring(content)

    pattern = re.compile(ur'(\b[^ ]{6}\b)', re.UNICODE)

    def walk_and_replace(element):
        if element.tag in ['script', 'style']:
            return

        if element.text:
            element.text = pattern.sub(ur'\1™', element.text)
        if element.tail:
            element.tail = pattern.sub(ur'\1™', element.tail)
        for child in element:
            walk_and_replace(child)

    elements_list = doc.xpath('//body')
    if elements_list:
        walk_and_replace(elements_list[0])
    return html.tostring(doc)


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
    import webbrowser
    webbrowser.open('http://0.0.0.0:8000', new=1)
    app.run(host='0.0.0.0', port=8000)
