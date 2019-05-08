# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from Scholarid.Scholarid.Savescid import Savescid


class PaperPipeline(object):
    def process_item(self, item):
        scid=item['scid']
        self.scmessage = Savescid('localhost', 27017, 'Scholar', 'scmessage')
        self.scmessage.collection.update({'scid':scid},{'$set':{'paper':item['paper']}})
        return item
