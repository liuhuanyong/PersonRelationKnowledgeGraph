#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: chenhe<hee0624@163.com>
# time: 2017-11-30
# version: 1.0

from html.parser import HTMLParser
from bs4 import BeautifulSoup

class StripParser(HTMLParser):
    """
    去除一些特定的标签
    """
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.drop_tags = {'script', 'style', 'iframe', 'aside', 'nav', 'footer'}
        self.fed = []
        self.point_tags =[]
        self.is_fed = True

    def handle_starttag(self, tag, attrs):
        if tag in self.drop_tags:
            self.is_fed = False
            self.point_tags.append(tag)
        else:
            if tag == 'p':
                tmp_attrs = ['{0}="{1}"'.format(i[0], i[1]) for i in attrs]
                tmp_attrs = ' '.join(tmp_attrs)

                self.fed.append('<p {}>'.format(tmp_attrs))
            else:
                self.fed.append('<{}>'.format(tag))

    def handle_data(self, data):
        if self.is_fed:
            self.fed.append(data)

    def handle_endtag(self, tag):
        if tag in self.drop_tags:
            if tag == self.point_tags[-1]:
                self.point_tags.pop()
            if not self.point_tags:
                self.is_fed = True
        else:
            self.fed.append('</{}>'.format(tag))

    def get_html(self):
        return '\n'.join(self.fed)


def pretty_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    fixed_html = soup.prettify()
    return fixed_html


def strip_tag(html):
    """
    去除html特定的标签
    :param html: string
    :return: string
    """
    s = StripParser()
    s.feed(html)
    return s.get_html()


def handle_html(html):
    html = pretty_html(html)
    html  = strip_tag(html)
    return html

