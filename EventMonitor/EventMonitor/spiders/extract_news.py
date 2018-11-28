#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
from collections import Counter
from operator import itemgetter
import copy
from lxml import etree
from .handle_html import *
from .utils import *

class NewsParser:
    def __init__(self):
        self.score = 6
        self.length = 5

    def _cal_score(self, text):
        """计算兴趣度"""
        if "。" not in text:
            if "，" in text:
                return 0
            else:
                return -1
        else:
            score = text.count('，') + 1
            score += text.count(',') + 1
            score += text.count('；')
            score += text.count('。')
            return score

    def _line_div(self, html):
        html = re.sub("</?div>|</?table>", "</div><div>", html, flags=re.I)
        html = html.replace('</div>', '', 1)
        index = html.rfind('<div>')
        html = html[:index] + html[index:].replace('<div>', '', 1)
        return html

    def _line_p(self, text):
        text_list = list()
        text = re.sub(r'</?p\s?.*?>', r'</p><p class="news_body">', text, flags=re.I | re.S)
        text = text.replace('</p>', '', 1)
        index = text.rfind('<p>')
        text = text[:index] + text[index:].replace('<p>', '', 1)
        text = '<p class="news_head">{0}</p>'.format(text)
        return text

    def _extract_paragraph(self, html):

        cluster_para = {}
        absorb_para = {}
        for index, div_str in enumerate(re.findall("<div>(.*?)</div>", html, flags=re.S | re.I)):
            if len(div_str.strip()) == 0:
                continue
            para_str = div_str.strip()
            score = self._cal_score(para_str)
            if score > self.score:
                cluster_para[index] = [para_str, score]
            else:
                absorb_para[index] = [para_str, score]
        return cluster_para, absorb_para

    def _extract_feature(self, para_dict):
        c = Counter()
        index, text = max(para_dict.items(), key=lambda asd: asd[1][1])
        feature_list = re.findall("(<p.*?>)", text[0], flags=re.I | re.S)
        for feature in feature_list:
            c[feature] += 1
        if c.most_common(1):
            feature, amount = c.most_common(1)[0]
        else:
            feature = ''
        feature = feature.replace('(', '\(').replace(')', '\)')
        return index, feature

    def _gen_skeleton(self, para_dict, index, feature):
        """ 聚类段落集聚类生成生成正文脉络集合"""
        skeleton_dict = {}
        num_list = []
        if not feature:
            skeleton_dict[index] = para_dict[index]
            return skeleton_dict
        for num in para_dict.keys():
            num_list.append(num)
        num_list = sorted(num_list)
        od = num_list.index(index)
        f_list = num_list[0:od]
        l_list = num_list[od:len(num_list)]
        # 向后聚类
        while l_list:
            tmp = l_list.pop(0)
            length = abs(tmp - index)
            if length < self.length:
                if re.match(r".*?{0}".format(feature), para_dict[tmp][0], flags=re.S | re.I):
                    skeleton_dict[tmp] = para_dict[tmp]
            index = tmp
        # 向前聚类
        while f_list:
            tmp = f_list.pop()
            length = abs(index - tmp)
            if length < self.length:
                if re.match(r".*?{0}".format(feature), para_dict[tmp][0], flags=re.S):
                    skeleton_dict[tmp] = para_dict[tmp]
            index = tmp
        return skeleton_dict

    def _absorb_text(self, skeleton_dict, para_dict):
        """从伪噪声段落吸收噪声段落"""
        content_dict = skeleton_dict
        sk_list = skeleton_dict.keys()
        pa_list = para_dict.keys()
        sk_list = sorted(sk_list)
        pa_list = sorted(pa_list)
        heads = []
        middle = []
        tail = []
        for each in pa_list:
            if each < sk_list[0]:
                heads.append(each)
            if each > sk_list[-1]:
                tail.append(each)
            if (each >= sk_list[0]) and (each <= sk_list[-1]):
                middle.append(each)
        while heads:
            tmp = heads.pop()
            index = sk_list[0]
            if abs(tmp - index) < self.length:
                if para_dict[tmp][1] * 2 > self.score:
                    content_dict[tmp] = para_dict[tmp]
            else:
                break
        while tail:
            tmp = tail.pop(0)
            index = sk_list[-1]
            if abs(tmp - index) < self.length:
                if para_dict[tmp][1] * 2 > self.score:
                    content_dict[tmp] = para_dict[tmp]
            else:
                break
        while middle:
            tmp = middle.pop()
            if para_dict[tmp][1] * 2 > self.score:
                content_dict[tmp] = para_dict[tmp]
        return content_dict

    def _substring(self, text):
        text = self._line_p(text)
        text = pretty_html(text)
        selector = etree.HTML(text)
        xpath_result = selector.xpath('//p')
        if len(xpath_result) == 1:
            sub_string = xpath_result[0].xpath('string(.)')
            sub_string = drop_mutil_br(sub_string)
        else:
            text_list = []
            xpath_result = selector.xpath('//p[@class="news_body"]')
            for item in xpath_result:
                p_string = item.xpath('string(.)').strip()

                if not p_string:
                    continue
                p_string = drop_null(p_string)
                text_list.append(p_string)
            if text_list:
                sub_string = '\n'.join(text_list)
            else:
                sub_string = ''
        return sub_string

    def _pretty_text(self, index_content_list):
        contents = list()
        for each in index_content_list:
            sub_text = self._substring(each[1][0])
            if not sub_text:
                continue
            else:
                contents.append(sub_text)
        text = "\n".join(contents)
        return text

    def extract_news(self, html):
        html = handle_html(html)
        html = self._line_div(html)
        index = 0
        cluster_para, absorb_para = self._extract_paragraph(html)
        if cluster_para:
            index, feature = self._extract_feature(cluster_para)
            skeleton_dict = self._gen_skeleton(cluster_para, index, feature)
            if skeleton_dict:
                if absorb_para:
                    content_dict = self._absorb_text(skeleton_dict, absorb_para)
                else:
                    content_dict = skeleton_dict
                index_content_list = sorted(content_dict.items(), key=itemgetter(0))

                top_div_list = list()
                top_text = ''
                index = index_content_list[0][0]
                for ind, each_div in enumerate(re.findall("<div>(.*?)</div>", html, flags=re.S)):
                    if ind >= index:
                        break
                    top_text += each_div
                    top_div_list.append((ind, each_div))
        else:
            return

        '''正文抽取'''
        def extract_content():
            text = ''
            if index_content_list:
                text = self._pretty_text(index_content_list)
                text = text.strip()
            return text

        '''发布时间抽取'''
        def extract_pubtime():
            pubtime = ''
            tmp_top_div_list = copy.deepcopy(top_div_list)
            while tmp_top_div_list:
                ind, item = tmp_top_div_list.pop()
                if not item.strip():
                    continue
                div_selector = etree.HTML(item)
                if div_selector is None:
                    continue
                div_text = div_selector.xpath('string(.)').strip()
                if not div_text:
                    continue
                pubtime = re.search(r'(\d{4}\s*[年\-:/]\s*)\d{1,2}\s*[月\-：/]\s*\d{1,2}\s*[\-_:日]?\s*\d{1,2}\s*:\s*\d{1,2}\s*(:\s*\d{1,2})?', div_text, flags=re.S|re.I)
                if pubtime:
                    pubtime = pubtime.group()
                    index = ind
                    break
            if not pubtime:
                tmp_top_div_list = copy.deepcopy(top_div_list)
                while tmp_top_div_list:
                    ind, item = tmp_top_div_list.pop()
                    if not item.strip():
                        continue
                    div_selector = etree.HTML(item)
                    if div_selector is None:
                        continue
                    div_text = div_selector.xpath('string(.)')
                    pubtime = re.search(r'(\d{4}\s*[年\-:/]\s*)\d{1,2}\s*[月\-：/]\s*\d{1,2}\s*[\-_:日/]?', div_text,
                                        flags=re.S)
                    if pubtime:
                        pubtime = pubtime.group()
                        index = ind
                        break
            if pubtime:
                pubtime = pubtime.strip()
                pubtime = pubtime.replace('年', '-').replace('月', '-').replace('日', ' ').replace('/', '-')
                pubtime = drop_mutil_blank(pubtime)
                return pubtime, index
            else:
                return pubtime, 0

        '''标题抽取'''
        def extract_title():
            title = ''
            selector = etree.HTML(html)
            tmps = selector.xpath('//title/text()')
            if tmps:
                title = tmps[0].strip()
                title = clear_title(title)
            return title

        news = {}
        news_content = extract_content()
        news_pubtime, index = extract_pubtime()
        news_title = extract_title()
        news['news_content'] = news_content
        news['news_pubtime'] = self.pretty_time(news_pubtime)
        if news['news_pubtime']:
            news['news_date'] = news['news_pubtime'].split(' ')[0]
        else:
            news['news_date'] = ''
        news['news_title'] = news_title

        if not (news['news_content'] and news['news_pubtime'] and news['news_title'] and news['news_date']):
            return {}

        return news

    '''时间标准化'''
    def pretty_time(self, time):
        if not time:
            return None
        modify_time = time
        if len(time.split(' ')) == 2:
            date = modify_time.split(' ')[0]
            hour = modify_time.split(' ')[1]
            date_new = self.pretty_date(date)
            modify_time = ' '.join([date_new, hour])
        else:
            date = modify_time.split(' ')[0]
            modify_time = self.pretty_date(date)

        return modify_time

    '''标准化年月日'''
    def pretty_date(self, date):
        date = date.split('-')
        if len(date) != 3:
            return ''
        year = date[0]
        month = date[1]
        day = date[2]
        if int(month) < 10 and len(month) == 1:
            month = '0' + month

        if int(day) < 10 and len(day) == 1:
            day = '0' + day
        date_new = '-'.join([year, month, day])
        return date_new





