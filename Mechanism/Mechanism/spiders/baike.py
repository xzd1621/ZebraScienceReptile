# -*- coding: utf-8 -*-
import os
from urllib.parse import urljoin, quote

import scrapy
from fake_useragent import UserAgent

from Mechanism.items import MechanismItem
from Scholarid.Scholarid.Savescid import Savescid


class BaikeSpider(scrapy.Spider):
    name = 'baike'
    # allowed_domains = ['https://baike.baidu.com/item/%E5%8C%97%E4%BA%AC%E8%88%AA%E7%A9%BA%E8%88%AA%E5%A4%A9%E5%A4%A7%E5%AD%A6']
    # start_urls = ['http://https://baike.baidu.com/item/%E5%8C%97%E4%BA%AC%E8%88%AA%E7%A9%BA%E8%88%AA%E5%A4%A9%E5%A4%A7%E5%AD%A6/']
    location=os.getcwd()+'\\fake_useragent.json'
    ua=UserAgent(path=location)
    headers={'User-Agent':ua}
    def mechanism2url(self,mechanism):
        return urljoin('https://baike.baidu.com/item/',quote(mechanism))

    def start_requests(self):
        self.scmessage=Savescid('localhost',27017,'Scholar','scmessage')
        self.mechanism=Savescid('localhost',27017,'Scholar','mechanism')
        count=0
        for mechanism in self.scmessage.getscmechanism():
            if self.mechanism.collection.find_one({'mechanism':mechanism})==None :
                count+=1
                print('开始爬取第'+str(count)+'个机构:'+mechanism)
                mechanismurl=self.mechanism2url(mechanism)
                yield scrapy.Request(url=mechanismurl,callback=self.parse,meta={'mechanism':mechanism,'url':mechanismurl})

    def textlist2str(self,textlist):
        temp = ''.join(i for i in textlist if '\n' not in i and '[' not in i)
        temp = ''.join(temp.split())
        return temp
    def parse(self, response):
        item=MechanismItem()
        item['mechanism']=response.meta['mechanism']
        item['url']=response.meta['url']
        #简介，每一个元素是一个段落
        item['introduction']=list()
        paras=response.css('.lemma-summary .para')
        for para in paras:
            item['introduction'].append(self.textlist2str(para.css('::text').extract()))
        yield item