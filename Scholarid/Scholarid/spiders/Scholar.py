# -*- coding: utf-8 -*-
import requests
import scrapy
from gevent import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from Scholarid.Savescid import Savescid
from Scholarid.items import ScholaridItem


class ScholarSpider(scrapy.Spider):
    name = 'Scholar'
    # allowed_domains = ['http://xueshu.baidu.com/scholarID/CN-B374BHLJ']
    # start_urls = ['http://http://xueshu.baidu.com/scholarID/CN-B374BHLJ/']

    def start_requests(self):
        self.sc = Savescid('localhost', 27017, 'Scholar', 'scid')
        self.idlist=list() #辨别此ID是否爬取过
        for id in self.sc.getscid():
            if id not in self.idlist:
                self.idlist.append(id)
                yield scrapy.Request(url=self.sc.scid2url(id),meta={'scid':id,'scurl':self.sc.scid2url(id)})
        self.sc=Savescid('localhost',27017,'Scholar','scmessage')
        for id in self.sc.getsccopid():
            if id not in self.idlist:
                self.idlist.append(id)
                yield scrapy.Request(url=self.sc.scid2url(id), meta={'scid': id, 'scurl': self.sc.scid2url(id)})

    '''
    网页中的网址转换为实际的网址
    '''
    def source2real(self,url):
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'}
        request=requests.get(url,headers=headers)
        return  request.url

    def parse(self, response):
        item=ScholaridItem()
        item['scid']=response.meta['scid']
        item['scurl']=response.meta['scurl']
        item['name']=response.css('.p_name ::text').extract_first()
        item['mechanism']=response.css('.p_affiliate ::text').extract_first()
        p_ach=response.css('.p_ach_num ::text').extract()
        item['citedtimes']=p_ach[0]
        item['resultsnumber']=p_ach[1]
        item['Hindex']=p_ach[2]
        item['Gindex']=p_ach[3]

        field=response.css('.person_domain ::text').extract()
        item['field']=list(filter(lambda x:x!='/',field))

        pie=response.css('.pieText .number ::text').extract()
        if len(pie)==4:
            item['journal']=pie[0]
            item['meeting']=pie[1]
            item['professionwork']=pie[2]
            item['other']=pie[3]
        else:
            item['journal']=''
            item['meeting']=''
            item['professionwork']=''
            item['other']=''

        item['total']=response.css('.pieMapTotal .number ::text').extract_first()

        #爬取关系网
        chrome_options=webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        browser=webdriver.Chrome(chrome_options=chrome_options)
        browser.get(response.request.url)
        item['copinfo'] = list()
        #如果有关系网图，就爬取图的，否则爬取侧栏的合作学者
        try :
            browser.find_element_by_css_selector('.co_author_wr h3 a').click() #模拟点击更多按钮
            time.sleep(0.5)
            sreach_window = browser.current_window_handle #重定位网页
            co_persons=browser.find_elements_by_css_selector('.co_relmap_person')
            for co_person in co_persons:
                person=dict()
                person['url']=self.source2real(co_person.get_attribute('href'))
                co_person=co_person.find_element_by_css_selector('.co_person_name')
                person['name']=co_person.text
                person['count']=co_person.get_attribute('paper-count') #合作次数
                person['mechanism']=co_person.get_attribute('affiliate')
                item['copinfo'].append(person)
        except NoSuchElementException:
            co_persons=response.css('.au_info')
            for co_person in co_persons:
                person=dict()
                person['url']=self.source2real('http://xueshu.baidu.com'+co_person.css('a::attr(href)').extract_first())
                person['name']=co_person.css('a ::text').extract_first()
                person['mechanism']=co_person.css('.au_label ::text').extract_first()
                person['count']=1 #暂定，网页并没有合作次数
                item['copinfo'].append(person)
        finally:
            browser.close()

        yield item