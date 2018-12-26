#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import os

# 验证文件位置，并返回内容和文件名
def Inspect():
    fname = sys.argv[1]  # 获取参数
    fpath = "./SkillFile/{0}.json".format(fname)
    if not os.path.exists(fpath):
        print("请将json文件放置在SkillFile文件夹下！")
        return -1
    with open(fpath, 'r', encoding='utf-8') as f:
        skills = json.load(f)
    return skills, str(fname).rsplit(".", 1)[0].strip()

# 合并关键字
def Merge(skills, fname):
    old_fname = "./SkillFile/{0}-技能点.json".format(fname)
    with open(old_fname, 'r', encoding='utf-8') as f:
        old_skills = json.load(f)   # 原始技能点
    result_dic = {}
    for sk in skills:   # 遍历关键字
        keys = str(sk).split('|')
        count = 0
        for k in keys:
            for old_sk in old_skills:
                if k.lower().strip() in str(old_sk[0]).lower().strip():
                    count += old_sk[1]
        result_dic[keys[0]] = count
    result = sorted(result_dic.items(), key=lambda item: item[1], reverse=True)
    savePath = "./SkillFile/{0}-目标文件.json".format(fname)
    with open(savePath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)
    print("完成！")

if __name__ == "__main__":
    skills, fname = Inspect()
    if skills != -1 and fname != "":
        Merge(skills, fname)