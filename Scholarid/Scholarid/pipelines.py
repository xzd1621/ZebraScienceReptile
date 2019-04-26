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

        '''
        首次运行就直接插入数据库即可
        因为在爬取开始时就已经判断该专家的ID是否已经被爬取过
        若是爬取后中断，再次运行插入数据库前就需要先判断数据库中是否已有
    
        '''
        if sc.collection.find_one({'scid':item['scid']})==None:
            sc.collection.insert(item)

        # sc.collection.insert(item)
        # self.post.insert(item)
        return item