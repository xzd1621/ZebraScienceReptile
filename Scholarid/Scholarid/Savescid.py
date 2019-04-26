'''
从txt文件中提取出ScholarID,存入mongodb中
'''
import re

import pymongo

class Savescid():
    def __init__(self,host,port,db,collection):
        self.host=host
        self.port=port
        self.client=pymongo.MongoClient(self.host,self.port)
        self.db=self.client[db]
        self.collection=self.db[collection]

    '''
        根据学者主页的url提取他的Scholarid
    '''
    def scurl2id(self,url):
        pattern = re.compile('scholarID\/(.*?)(\?.*?|\s|\Z)')
        results = pattern.findall(url)
        for result in results:
            if len(result) > 0:
                return result[0]
            else:
                print('url转id错误！')
                return ''

    '''
    根据学者Scholarid构造其主页url
    '''
    def scid2url(self,id):
        return 'http://xueshu.baidu.com/scholarID/' + id

    def save_Mongo(self, txtfile):
        with open(txtfile, 'r+', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                scid=self.scurl2id(line)
                self.collection.insert({'scid': scid,'scurl':self.scid2url(scid)})

    '''
    从数据库中取出scholarid
    '''
    def getscid(self):
        for item in self.collection.find():
            yield item['scid']

    def getsccopid(self):
        for item in self.collection.find():
            if len(item['copinfo']) >0:
                for person in item['copinfo']:
                    yield self.scurl2id(person['url'])
            else:
                continue

    '''
    将从网页中爬取的scid和用户主页链接插入数据库，插入之前先查询数据库是否已有
    '''
    def insertid(self,scurl):
        scid=self.scurl2id(scurl)
        if self.collection.find_one({'scid':scid},no_cursor_timeout = True)==None:
            self.collection.insert({'scid': scid, 'scurl': self.scid2url(scid)})

if __name__ == '__main__':
    sc=Savescid('localhost',27017,'Scholar','scid')
    sc.save_Mongo('scholarid_url.txt')