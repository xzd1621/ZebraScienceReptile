# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from Scholarid.Scholarid.Savescid import Savescid


class MechanismPipeline(object):
    def process_item(self, item, spider):
        self.mechanism = Savescid('localhost', 27017, 'Scholar', 'mechanism')
        self.mechanism.collection.insert(dict(item))
        return item
