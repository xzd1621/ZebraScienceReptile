# -*- coding: utf-8 -*-
import json
import os
import re
import time

from fake_useragent import UserAgent

from lxml import etree

import requests
from Paper.items import PaperItem
import scrapy
import copy

from Scholarid.Scholarid.Savescid import Savescid

class ZebrapaperSpider(scrapy.Spider):
    name = 'Zebrapaper'
    base_url='http://xueshu.baidu.com'
    location = os.getcwd() + '\\fake_useragent.json'
    ua = UserAgent(path=location)
    headers = {'User-Agent': ua.random}
    # allowed_domains = ['http://xueshu.baidu.com/s?wd=%E7%8E%8B%E6%96%8C%20%22%E4%B8%AD%E5%9B%BD%E4%BA%BA%E6%B0%91%E5%A4%A7%E5%AD%A6%E6%96%B0%E9%97%BB%E5%AD%A6%E9%99%A2%22%20author%3A%28%E7%8E%8B%E6%96%8C%29']
    # start_urls = ['http://http://xueshu.baidu.com/s?wd=%E7%8E%8B%E6%96%8C%20%22%E4%B8%AD%E5%9B%BD%E4%BA%BA%E6%B0%91%E5%A4%A7%E5%AD%A6%E6%96%B0%E9%97%BB%E5%AD%A6%E9%99%A2%22%20author%3A%28%E7%8E%8B%E6%96%8C%29/']
    def start_requests(self):
        self.scmessage = Savescid('localhost', 27017, 'Scholar', 'scmessage')
        self.paper=Savescid('localhost',27017,'Scholar','paper')
        for scurl in self.scmessage.getscurl():
            scid = self.scmessage.scurl2id(scurl)
            yield scrapy.Request(url=scurl,meta={'scid':scid},callback=self.parse_list,headers=self.headers)

    def paperid2url(self,paperid):
        return 'http://xueshu.baidu.com/usercenter/paper/show?paperid='+paperid

    #爬取学者主页下的论文列表
    def parse_list(self,response):
        is_hasnext=True
        #获取专家论文列表最大的页数
        try:
            max_page=int(response.css('.pagenumber ::text').extract()[-1])
            author_url = 'http://xueshu.baidu.com/usercenter/data/author'
            for index in range(1, max_page + 1):
                form_data = {
                    'cmd': 'academic_paper',
                    'entity_id': '',
                    'bsToken': '07d57f29985111be7bc2ecb0be738da8',
                    'curPageNum': str(index),
                }
                # 获取entity_id，其唯一确定一个学者
                r = requests.get(response.request.url,headers=self.headers)
                r.raise_for_status()
                html = etree.HTML(r.text)
                html = etree.tostring(html).decode('utf-8')
                search_entity_id = re.search('entity_id: \'(.*?)\',', html)
                entity_id = ''
                if search_entity_id:
                    entity_id = search_entity_id.group(1)
                form_data['entity_id'] = entity_id

                # 再次请求，得到以后每页论文列表
                r = requests.post(author_url, data=form_data,timeout=1,headers=self.headers)
                r.raise_for_status()
                html = etree.HTML(r.text)
                year_list = html.xpath('//span[@class="res_year"]/text()')
                pattern = re.compile(r'data-longsign="(.*?)"')
                results = pattern.findall(r.text)
                paperid_list = list()
                for result in results:
                    if len(result) > 0:
                        paperid_list.append(result)
                print('该页论文数'+str(len(paperid_list)))

                if len(paperid_list) > 0 and len(year_list) > 0:
                    count=0
                    for paperid, year in zip(paperid_list, year_list):
                        count+=1
                        if count==len(paperid_list) and index==max_page:
                            is_hasnext=False
                        print(response.request.url + '的第' + str(index) + '页  ' + self.paperid2url(paperid))
                        yield scrapy.Request(url=self.paperid2url(paperid), callback=self.parse,headers=self.headers,
                                             meta={'scid': response.meta['scid'], 'paperid': paperid, 'year': year,'is_hasnext':is_hasnext})
        except Exception:
            paperid_list=response.xpath('//div[@class="reqdata"]/@data-longsign').extract()
            print('paperid_list的长度:'+str(len(paperid_list)))
            year_list=response.css('.res_year ::text').extract()
            if len(paperid_list) > 0 and len(year_list) > 0:
                count=0
                for paperid, year in zip(paperid_list, year_list):
                    count+=1
                    if count==len(paperid_list):
                        is_hasnext=False
                    print(response.request.url+ '仅有1页  ' + self.paperid2url(paperid))
                    yield scrapy.Request(url=self.paperid2url(paperid), callback=self.parse,headers=self.headers,
                                         meta={'scid': response.meta['scid'], 'paperid': paperid, 'year': year,'is_hasnext':is_hasnext})

    #爬取论文的主页面
    def parse(self, response):
        #插入paper表格
        paper=dict()
        source_journal=dict()
        #论文的名字，paperid，年份，全部来源链接，来源期刊，免费下载链接，作者，摘要，关键词
        paper['name'] = response.css('.main-info h3 a::text').extract_first()
        paper['paperid']=response.meta['paperid']
        paper['year']=response.meta['year']
        paper['source_url'] =  response.css('.allversion_content .dl_item_span a[class="dl_item"]::attr(href)').extract()
        source_journal['name']=response.css('.journal_title ::text').extract_first()
        source_journal['date']= response.css('.journal_content ::text').extract_first()
        paper['source_journal']=source_journal
        paper['free_download_url']=response.css('#savelink_wr .dl_item_span a::attr(href)').extract()
        paper['author'] = response.css('.author_text a::text').extract()
        paper['abstract'] = response.xpath('//p[@class="abstract"]/text()').extract_first()
        paper['keyword'] = response.css('.kw_main a::text').extract()
        print(paper)
        # self.paper.collection.insert(paper)
        if self.paper.collection.find_one({'paperid':paper['paperid']})==None:
            self.paper.collection.insert(paper)
        # ZebrapaperSpider.item['paper'].append(paper)
        # ZebrapaperSpider.item['scid']=response.meta['scid']
        # if response.meta['is_hasnext']==False:
        #     temp_item=copy.deepcopy(ZebrapaperSpider.item)
        #     ZebrapaperSpider.item.clear()
        #     ZebrapaperSpider.item['paper'] = []
        #     print('爬取论文数'+str(len(temp_item['paper'])))
        #     yield temp_item
        temp_paper_list=self.scmessage.collection.find_one({'scid':response.meta['scid']})['paper']
        temp_paperid_list=list()
        for item in temp_paper_list:
            temp_paperid_list.append(item['paperid'])
        if paper['paperid'] not in temp_paperid_list and paper['name']!=None:
            temp_paper_list.append(paper)
        self.scmessage.collection.update({'scid':response.meta['scid']},{'$set':{'paper':temp_paper_list}})