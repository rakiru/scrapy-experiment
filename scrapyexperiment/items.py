# coding=utf-8

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MusicCDItem(scrapy.Item):
    title = scrapy.Field()
    artist = scrapy.Field()
    price = scrapy.Field()
