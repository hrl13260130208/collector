import re
import os
import uuid
import requests
import faker
from bs4 import BeautifulSoup
import PyPDF2
import redis

fake = faker.Factory.create()

first_dir = "C:/pdfs/"
redis_ = redis.Redis(host="10.3.1.99", port=6379 ,decode_responses=True)
finsh_name="t_download"
delete_name="delete"
url_dict="urls_dict"

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

def download():
    file=open("C:/pdfs/url.txt")
    for url in file.readlines():
        url=url.replace("\n","")

        data=requests.get(url,headers=header,timeout=20)
        soup=BeautifulSoup(data.text,"html.parser")
        for u in soup.find_all("a"):
            pdf_url=u["href"]
            if pdf_url == "#":
                p = re.search("location\.href='.*';", str(u))
                if p != None:
                    pdf_url=p.group()[15:-2]
            print("测试url:"+pdf_url)
            if redis_.sadd(url_dict,pdf_url) ==1:
                try:
                    pdf = requests.get(pdf_url, headers=header, verify=False, timeout=30)
                except:

                    pdf_url=url[:url.rfind("/")]+u["href"][1:]
                    print("新url:"+pdf_url)
                    pdf=requests.get(pdf_url, headers=header, verify=False, timeout=30)
                pdf.encoding = 'utf-8'
                file_name=creat_filename(create_dir("0410"))
                file = open(file_name, "wb+")
                file.write(data.content)
                page=-1
                try:
                    page=checkpdf(file_name)
                except:
                    print("链接有误！")
                    redis_.lpush(delete_name,file_name)
                if page>0:
                    print("已下载数据： "+pdf_url+"  "+file_name)
                    redis_.lpush("t_download",pdf_url+" "+file_name)

    print("链接已完成，开始写数据...")
    write_file=open("C:/pdfs/list.txt","a+")

    while(True):
        string = redis_.lpop(finsh_name)
        if string == None:
            break
        write_file.write(string+"\n")
    while(True):
        string = redis_.lpop(delete_name)
        if string == None:
            break
        os.remove(string)

    write_file.close()



if __name__ == '__main__':
    download()
    # print(redis_.sadd(url_dict)
    # print(redis_.llen(finsh_name))
    # print(redis_.smembers(url_dict))
    # redis_.delete(finsh_name)
    # redis_.delete(url_dict)

