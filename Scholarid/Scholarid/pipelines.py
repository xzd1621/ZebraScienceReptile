# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from Scholarid.Savescid import Savescid
from Scholarid.spiders.Scholar import ScholarSpider


class ScholaridPipeline(object):
    # def __init__(self):
    #     host = 'localhost'
    #     port = 27017
    #     dbname = 'Scholar'
    #     sheetname = 'scmessage'
    #     client = pymongo.MongoClient(host=host, port=port)
    #     mydb = client[dbname]
    #     self.post = mydb[sheetname]

    def process_item(self, item, spider):
        item=dict(item)
        sc=Savescid('localhost',27017,'Scholar','scmessage')
        sc.collection.insert(item)
        # self.post.insert(item)
        return item