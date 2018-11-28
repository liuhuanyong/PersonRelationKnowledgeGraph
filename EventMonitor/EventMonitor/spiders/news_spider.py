#!/usr/bin/env python3
# coding: utf-8
# File: news_spider.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-7-15

import scrapy
import os
from lxml import etree
import urllib.request
from urllib.parse import quote, quote_plus
from .extract_news import *
from EventMonitor.items import EventmonitorItem
import redis
import os

class BuildData:
    def __init__(self):
        cur = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.rel_filepath = os.path.join(cur, 'rel_data.txt')
        self.seed_rels = self.collect_rels()
        return

    '''加载关系数据集'''
    def collect_rels(self):
        rels_data = []
        for line in open(self.rel_filepath):
            line = line.strip().split('###')
            keywords = line[:-2]
            rels_data.append(keywords)
        return rels_data


class NewsSpider(scrapy.Spider):
    name = 'eventspider'
    def __init__(self):
        self.seed_rels = BuildData().seed_rels
        self.parser = NewsParser()
        self.pool = redis.ConnectionPool(host='192.168.1.29', port=6379, decode_responses=True)
        self.conn = redis.Redis(connection_pool=self.pool)
        self.redis_key = 'person_names'

    '''采集主函数'''
    def start_requests(self):
        while(1):
            res = self.conn.spop(self.redis_key)
            print(res)
            if str(res) == 'None':
                return
            line = res.strip().split('###')
            keywords = line[:-1]
            search_body = '+'.join([quote_plus(wd) for wd in keywords[:-1]])
            seed_urls = []
            for page in range(0, 101, 20):
                url = 'https://www.baidu.com/s?ie=utf-8&cl=2&rtt=1&bsst=1&tn=news&word=' + search_body + '&tngroupname=organic_news&pn=' + str(
                    page)
                seed_urls.append(url)
            for seed_url in seed_urls:
                param = {'url': seed_url,
                         'keyword': ' '.join(keywords)}
                yield scrapy.Request(url=seed_url, meta=param, callback=self.collect_newslist, dont_filter=True)

    '''获取新闻列表'''
    def collect_newslist(self, response):
        selector = etree.HTML(response.text)
        news_links = selector.xpath('//h3[@class="c-title"]/a/@href')
        print(response.meta['keyword'], len(set(news_links)))
        for news_link in news_links:
            param = {'url': news_link,
                     'keyword': response.meta['keyword']}
            yield scrapy.Request(url=news_link, meta=param, callback=self.page_parser, dont_filter=True)


    '''对网站新闻进行结构化抽取'''
    def page_parser(self, response):
        data = self.parser.extract_news(response.text)
        if data:
            item = EventmonitorItem()
            item['keyword'] = response.meta['keyword']
            item['news_url'] = response.meta['url']
            item['news_time'] = data['news_pubtime']
            item['news_date'] = data['news_date']
            item['news_title'] = data['news_title']
            item['news_content'] = data['news_content']
            yield item
        return
