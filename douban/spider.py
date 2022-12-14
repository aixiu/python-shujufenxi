# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Aixiu
# @Time  : 2022/10/29 11:22:18

# 视频地址：https://www.bilibili.com/video/BV12E411A7ZQ/?p=16&vd_source=20f7c1f5f32f90ae92d9428e45039d9b

from bs4 import BeautifulSoup  # 网页解析，获取数据
import re  # 正则表达式，进行文字匹配
import urllib.request, urllib.error  # 制定URL，获取网页数据
import xlwt  # 进行 excel 文件写入操作   Excel的写插件  安装命令：pip install xlwt；  Excel的读取插件  安装命令：pip install xlrd
import sqlite3  #  进行SQLite数据库操作

def main():
    baseurl = "https://movie.douban.com/top250?start={}"  # 基础 URL
    # 1.爬取网页
    datalist = getData(baseurl)
    savepath = f"./豆瓣电影Top250.xls"
    
    # 3.保存数据到 excel
    saveData(datalist, savepath)
    
    # askURL("https://movie.douban.com/top250?start=0")

# 影片详情链接的规则
findLink = re.compile(r'<a href="(.*?)">')   
# 创建正则表达式对象，表示规则（字符串的模式）   
# .*? 是满足条件的情况只匹配一次

# 影片图片链接的规则
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)   #  re.S 忽略换行符，让换行符包含在字符中

# 影片的片名
findTitle = re.compile(r'<span class="title">(.*)</span>')

# 影片的评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')

# 影片评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')

# 影片概况
findInq = re.compile(r'<span class="inq">(.*)</span>')

# 影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


# 爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0, 10):  # 调用获取页面信息的函数，10次
        url = baseurl.format(str(i * 25))
        html = askURL(url)  # 保存获取到的网页源码
        
        # 2.逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("div", class_="item"):   # 查找符合要求的字符串，形成列表  比如：class为 item的 div
            # print(item)  # 测试查看电影 item 全部信息
            data = []  # 保存一部电影的所有信息
            item =  str(item)
            
            # 获取影片详情的超链接
            link = re.findall(findLink, item)[0]  # re库用来通过正则表达式查找指定的字符串
            data.append(link)   # 添加链接
            
            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)  # 添加图片
            
            titles = re.findall(findTitle, item)
            if len(titles)  == 2:
                ctitle = titles[0]
                data.append(ctitle)  # 添加中文名
                otitle = titles[1].replace("/", "") # 去掉无关的符号
                data.append(otitle.strip())  # 添加外文名
            else:
                data.append(titles[0])
                data.append(" ")   # 外文名字留空
                
            rating = re.findall(findRating, item)[0]
            data.append(rating)  # 添加评分
            
            judgeNum = re.findall(findJudge, item)[0]
            data.append(judgeNum)  # 添加评价人数
            
            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")  #去掉句号
                data.append(inq)  # 添加概述
            else:
                data.append(" ")  # 留空
                
            bd = re.findall(findBd, item)[0]
            bd = re.sub("<br(\s+)?/>(\s+)?", " ", bd)  #去掉<br/>
            bd =  re.sub("/", " ", bd)  # 替换 /
            data.append(bd.strip())  # 去掉前后空格
            
            datalist.append(data)  # 把处理好的一部电影信息放入datalist
            
    # print(datalist)   # 测试打印获取到的信息
    return datalist

# 得到指定一个 url 的网页内容
def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50"
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):   # hasattr() 函数用于判断对象是否包含对应的属性。
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
            
    return html

# 保存数据
def saveData(datalist, savepath):
    print("save....")
    book = xlwt.Workbook(encoding="utf-8")  # 创建kook 对象 相当于一个excel文件
    sheet = book.add_sheet("豆瓣电影Top250", cell_overwrite_ok=True)  # 相当于在 excel 文件中创建一个表
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外国名", "评分", "评价数", "概况", "相关信息")
    
    for i in range(0, len(col)):
        sheet.write(0, i, col[i])  # 列名
        
    for i in range(0, 250):
        print(f"第{i+1}条")
        data = datalist[i]
        for j in range(0, len(col)):
            sheet.write(i+1, j, data[j])  # 每一列的数据        

    book.save(savepath)   # 保存到文件
    
if __name__ == '__main__':  # 当程序执行时
    # 调用函数
    main()
    print("爬取完毕!")