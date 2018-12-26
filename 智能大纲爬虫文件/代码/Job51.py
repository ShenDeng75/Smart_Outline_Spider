#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 根据岗位，得到岗位技能点
from multiprocessing.pool import ThreadPool

from lxml import html
import requests
import jieba
jieba.set_dictionary("./depend/dict.txt")
jieba.initialize()
import jieba.posseg as pseg
import os
import json
import jieba.analyse
jieba.analyse.set_stop_words("./depend/stop_word.txt")
import sys

global one
one = 1
class Get_SPofPost:
    # ----------初始化------------
    def __init__(self):
        self.results = []  # 最终结果（清洗后）
        self.count = 0     # 爬取的招聘信息总数
        self.gwName = ""  # 岗位名
        self.mstring = ""   # 待清洗的数据
        self.ip_list = []   # 代理ip
        self.k = 1
        self.old_url = set()
        # 请求头
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
    # ----------得到招聘链接-------
    def get_recruit(self, url):
        page = requests.get(url)
        tree = html.fromstring(page.text)
        # 获得所有岗位
        urls = tree.xpath(r'.//div[@class="el"]/p/span/a/@href')
        pool = ThreadPool(10)
        pool.map(self.UrlToMessage, urls)
        pool.close()
        pool.join()
        # 如果存在下一页
        next_page = tree.xpath(r'.//li[@class="bk"]/a/@href')
        if next_page:
            if next_page[-1] not in self.old_url:
                self.old_url.add(next_page[-1])
                self.get_recruit(next_page[-1])  # 递归遍历所有页

    # ----------得到岗位需求---------
    def UrlToMessage(self, url):
        global one
        if self.k == 0 and one == 1:
                print("网页需要验证....请前往验证 %s \n完成验证后按回车键继续"%(url))
                one = 0
                input()
                self.k = 1
        if self.k == 1:
           self.count += 1
           print("已爬取的招聘岗位数："+str(self.count))
           try:
               page = requests.get(url)
           except:
               print("该页有格式错误")
               return
           tree = html.fromstring(page.text)
           Messages = tree.xpath(r'.//div[@class="bmsg job_msg inbox"]//text()')
           ls_gw = ['条件', '职责', '要求', '任职', '资格', '招聘']
           ok = 0
           for m in Messages:
               ls_key = ['能力', '具备', '熟悉', '掌握', '熟练', '经验', '了解', '精通']
               if ok == 1:
                   if m[0] >= '0' and m[0] <= '9':
                       for k in ls_key:  # 关键字过滤
                           if k in m:
                               m = m[1:]
                               self.mstring += m
                   else:
                       break
               for gw in ls_gw:  # 关键字过滤
                   if gw in m:
                       ok = 1
    # -----------得到技能点------------
    def MessageTojieba(self, mstr):
        ans = pseg.lcut(mstr)
        for i in range(len(ans)):
            if ans[i].word in ['能力', '经验']:  # 后缀过滤
                sp = ""
                for j in range(i, i - 6, -1):
                    if ans[j].flag == 'x' or ans[j].word in ['有', '和']:
                        break
                    else:
                        sp = ans[j].word + sp
                    if j <= 0:
                        break
                if sp != "能力":
                    self.results.append(sp)
            if ans[i].word in ['具备', '精通', '熟练', '熟悉']:  # 前缀过滤
                sp2 = ""
                for j in range(i + 1, i + 6):
                    if ans[j].flag == 'x' or ans[j].word in ['有', '和']:
                        break
                    else:
                        sp2 = sp2 + ans[j].word
                    if j+1 >= len(ans):
                        break
                if len(sp2) != 0:
                    self.results.append(sp2)
            if ans[i].word in ['良好的', '较强的', '强烈的', '一定']:  # 前缀过滤
                sp3 = ""
                for j in range(i, i + 6):

                    if ans[j].flag == 'x' or ans[j].word in ['有', '和', '.']:
                        break
                    else:
                        sp3 = sp3 + ans[j].word
                    if j+1 >= len(ans):
                        break
                if len(sp3) != 0:
                    self.results.append(sp3)
def Start():
    obj = Get_SPofPost()
    obj.gwName = sys.argv[1]   # 获得参数
    url = str.format("https://search.51job.com/list/000000,000000,0000,00,9,99,{0},2,1.html", obj.gwName)
    obj.get_recruit(url)
    obj.MessageTojieba(obj.mstring)

    # 写入Json文件
    dic = {}
    for a in set(obj.results):
        dic[a] = obj.results.count(a)
    dic_list = sorted(dic.items(), key=lambda item: item[1], reverse=True)
    if not os.path.exists("./SkillFile"):
        os.mkdir("./SkillFile")
    path = str.format(r"./SkillFile/{0}-技能点.json", obj.gwName)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dic_list, f, ensure_ascii=False)
    print("---技能点文件已保存到：" + path + "\n")

    return path, obj.gwName

# 获取高频词汇
def jnd_jieba(fpath, fname):
   with open(fpath, 'r', encoding='utf-8') as f:
       skills = json.load(f)
   mstring = ""
   for sk in skills:
       for i in range(int(sk[1])):
           mstring += sk[0] + "。"

   gjz = jieba.analyse.extract_tags(mstring.lower(), 100)
   print("\n".join(gjz))
   savePath = r"./SkillFile/{0}-高频词汇.json".format(fname)
   with open(savePath, 'w', encoding='utf-8') as f:
       json.dump(gjz, f, ensure_ascii=False)

   print("---前100个高频词汇已保存到：" + savePath)
   return gjz

if __name__ == "__main__":
    fpath, fname = Start()
    jnd_jieba(fpath, fname)
