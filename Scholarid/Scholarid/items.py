# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScholaridItem(scrapy.Item):
    # define the fields for your item here like:
    scid=scrapy.Field() #学者Scholarid
    scurl=scrapy.Field() #学者主页url
    name = scrapy.Field() #学者名字
    mechanism=scrapy.Field() #学者机构
    citedtimes=scrapy.Field() #被引频次
    resultsnumber=scrapy.Field() #成果数量
    Hindex=scrapy.Field() #H指数
    Gindex=scrapy.Field() #G指数
    field=scrapy.Field() #领域，数组类型，可能不止一个领域
    journal=scrapy.Field() #期刊
    meeting=scrapy.Field() #会议
    professionwork=scrapy.Field() #专著
    other=scrapy.Field() #其它
    total=scrapy.Field() #总计
    copinfo=scrapy.Field() #与该学者合作的学者的信息
    paper=scrapy.Field() #论文信息