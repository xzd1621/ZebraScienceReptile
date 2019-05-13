# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MechanismItem(scrapy.Item):
    # define the fields for your item here like:
    mechanism = scrapy.Field() #机构名字
    url=scrapy.Field() #机构百度百科链接
    introduction=scrapy.Field() #机构简介