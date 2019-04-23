import re
import os
import uuid
import requests
import faker
from bs4 import BeautifulSoup
import PyPDF2
import redis
import time
import random
import logging

fake = faker.Factory.create()
logger=logging.getLogger("logger")

first_dir = "C:/pdfs/"
# name="1"
name="2"
url_file="C:/pdfs/url2.txt"
# url_file="C:/pdfs/url.txt"
redis_ = redis.Redis(host="10.3.1.99", port=6379 ,db=6,decode_responses=True)
finsh_name="t_download_"+name
delete_name="delete_"+name
url_dict="urls_dict_"+name


def create_dir(dir_name):
    # first_dir = "F:/pdfs/"

    dir = first_dir +dir_name + "/"
    if not os.path.exists(dir):
        if not os.path.exists(first_dir):
            os.mkdir(first_dir)
        os.mkdir(dir)
    return dir

def creat_filename(dir):
    uid=str(uuid.uuid1())
    suid=''.join(uid.split('-'))
    return dir+suid+".pdf"

header={"User-Agent": fake.user_agent(),
        "Upgrade-Insecure-Requests": "1",
        "If-Modified-Since": "Tue, 10 May 2016 01:04: 09 GMT",
        "If-None-Match": "2bba-53272809d3440-gzip"
}

def checkpdf(file):
    pdf = PyPDF2.PdfFileReader(open(file,"rb"),strict=False)
    return pdf.getNumPages()

def wait():
    time.sleep(random.random() * 3+1)

def download():
    file=open(url_file)
    for url in file.readlines():
        url=url.replace("\n","")

        data=requests.get(url,headers=header,timeout=20)
        soup=BeautifulSoup(data.text,"html.parser")
        for u in soup.find_all("a"):
            file_name = creat_filename(create_dir("0410"))
            try:
                pdf_url=u["href"]
                if "#" in pdf_url:
                    p = re.search("location\.href='.*';", str(u))
                    if p != None:
                        pdf_url=p.group()[15:-2]
                print("测试url:"+pdf_url)

                if redis_.sadd(url_dict,pdf_url) ==1:
                    wait()
                    pdf = requests.get(pdf_url, headers=header, verify=False, timeout=30)
                    pdf.encoding = 'utf-8'

                    file = open(file_name, "wb+")
                    file.write(pdf.content)
                    file.close()
            except:
                logger.info("err",exc_info = True)
                try:
                    pdf_url="https://dynamic-positioning.com"+u["href"]
                    print("新url:"+pdf_url)
                    wait()
                    pdf=requests.get(pdf_url, headers=header, verify=False, timeout=30)
                    pdf.encoding = 'utf-8'
                    file = open(file_name, "wb+")
                    file.write(pdf.content)
                    file.close()
                except:
                    logger.info("err", exc_info=True)
                    pass

            page=-1
            try:
                print("检查pdf")
                page=checkpdf(file_name)
                print("pdf页数："+page)
            except:
                print("链接有误！")
                redis_.lpush(delete_name,file_name)
            if page>0:
                print("已下载数据： "+pdf_url+"  "+file_name)
                redis_.lpush("t_download",pdf_url+" "+file_name)

    print("链接已完成，开始写数据...")
    write()


def write():
    write_file = open("C:/pdfs/list" + name + ".txt", "a+")

    while (True):
        string = redis_.lpop("t_download")
        if string == None:
            break
        write_file.write(string + "\n")
    # while (True):
    #     string = redis_.lpop(delete_name)
    #     if string == None:
    #         break
    #     try:
    #         os.remove(string)
    #     except:
    #         pass

    write_file.close()

if __name__ == '__main__':
    download()
    # write()
    # file_name="C:/pdfs/test.pdf"
    # url="https://j-nav.org/download/k139-02/?wpdmdl=3056"
    # pdf = requests.get(url, headers=header, verify=False, timeout=30)
    # pdf.encoding = 'utf-8'
    #
    # file = open(file_name, "wb+")
    # file.write(pdf.content)
    # file.close()
    # page = checkpdf(file_name)
    # print(page)
    #
    # write()
    # print(redis_.sadd(url_dict))
    # print(redis_.llen("t_download"))
    # print(redis_.smembers(url_dict))
    # redis_.delete(finsh_name)
    # redis_.delete(url_dict)


