'''
从txt文件中提取出ScholarID,存入mongodb中
'''
import re
from urllib.parse import quote,unquote
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
    从数据库中取学者主页url
    '''
    def getscurl(self):
        for item in self.collection.find():
            yield item['scurl']

    '''
    从数据库中取学者的名字和机构来构造url查询他的所有论文
    根据ID来插入学者信息表
    '''
    def getscpaperurl(self):
        for item in self.collection.find():
            if item['name']!=None and item['mechanism']!=None:
                yield  ('http://xueshu.baidu.com/s?wd='+quote(item['name']+' "'+item['mechanism']+'" author:('+item['name']+')'),item['scid'])
            else:
                continue

    '''
    将从网页中爬取的scid和用户主页链接插入数据库，插入之前先查询数据库是否已有
    '''
    def insertid(self,scurl):
        scid=self.scurl2id(scurl)
        if self.collection.find_one({'scid':scid},no_cursor_timeout = True)==None:
            self.collection.insert({'scid': scid, 'scurl': self.scid2url(scid)})

    '''
    复制表，将source复制到goal
    '''
    # def copy(self,source,goal):
    #     for item in source.collection.find():
    #         goal.collection.insert(item)

if __name__ == '__main__':
    sc=Savescid('localhost',27017,'Scholar','scmessage')
    # print(unquote('http://xueshu.baidu.com/s?wd=%E6%9D%A8%E6%99%93%E5%85%89%20%22%E5%90%8C%E6%B5%8E%E5%A4%A7%E5%AD%A6%E4%BA%A4%E9%80%9A%E8%BF%90%E8%BE%93%E5%B7%A5%E7%A8%8B%E5%AD%A6%E9%99%A2%22%20author%3A%28%E6%9D%A8%E6%99%93%E5%85%89%29&pn=200'))
    # count=0
    # for url in sc.getscpaperurl():
    #     print(url)
    #     count+=1
    # print(count)
    # sc.save_Mongo('scholarid_url.txt')
    # sccopy=Savescid('localhost',27017,'Scholar','scmessagecopy')
    # sc.collection.drop()
    # for item in sccopy.collection.find():
    #     sc.collection.insert(item)

    for item in sc.collection.find():
        sc.collection.update({'scid':item['scid']},{'$set':{'paper':[]}})

    # item= sc.collection.find_one({'scid':'CN-BQ74RHWJ'})
    # namelist=list()
    # for paper in item['paper']:
    #     if paper['name']!=None:
    #         print(paper['name'])
    #         namelist.append(paper['name'])
    # print(len(namelist))
