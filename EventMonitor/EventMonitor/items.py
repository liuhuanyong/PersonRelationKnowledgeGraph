# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EventmonitorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    keyword = scrapy.Field()
    news_url = scrapy.Field()
    news_time = scrapy.Field()
    news_date = scrapy.Field()
    news_title = scrapy.Field()
    news_content = scrapy.Field()