#!/usr/bin/env python
# encoding: utf-8
'''
@author: Kunchnag Li
@contact: 812487273@qq.com
@file: try_spider.py
@time: 2019/5/7 12:04
@desc:
'''
import re
import json
import requests
import pprint

paperid_list = list()
for curPagenum in range(1,36):
    form_data = {
        "cmd": "academic_paper",
        "entity_id": "57fa4bcb10f25dc179839a988c3be2e1",
        "bsToken": "07d57f29985111be7bc2ecb0be738da8",
        "curPageNum": str(curPagenum),
    }
    print(form_data)
    url = "http://xueshu.baidu.com/usercenter/data/author"

    response = requests.post(url, data=form_data, timeout=1)
    pattern = re.compile(r'data-longsign="(.*?)"')
    results = pattern.findall(response.text)
    every_page_list=list()
    for result in results:
        if len(result) > 0:
            every_page_list.append(result)
            paperid_list.append(result)
    print(str(curPagenum)+"论文数量："+str(len(every_page_list)))
print(paperid_list)
print(len(paperid_list))

# form_data={
#     'cmd': 'academic_paper',
#     'entity_id': "'cb7812c8428497d80cb850ba921365ff'",
#     'bsToken': '07d57f29985111be7bc2ecb0be738da8',
#     'curPageNum': '1'
# }

# pprint.pprint(response.text)
