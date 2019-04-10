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
            pdf = requests.get(pdf_url, headers=header, verify=False, timeout=30)

            if pdf.status_code != 200:
                pdf_url=url[:url.rfind("/")]+u["href"]
                pdf=requests.get(pdf_url, headers=header, verify=False, timeout=30)
            pdf.encoding = 'utf-8'
            file_name=creat_filename(create_dir("0410"))
            file = open(file_name, "wb+")
            file.write(data.content)
            page=-1
            try:
                page=checkpdf(file_name)
            except:
                pass
            if page>0:
                redis_.lpush("t_download",pdf_url+" "+file_name)

    write_file=open("C:/pdfs/list.txt","a+")
    while(True):
        string = redis_.lpop("t_download")
        if string == None:
            break
        write_file.write(string+"\n")

    write_file.close()







print(creat_filename(create_dir("d")))

if __name__ == '__main__':
    # download()
    url="https://j-nav.org/presentation-paper/presentation-paper-2017-2/"
    data = requests.get(url, headers=header, timeout=20)
    soup = BeautifulSoup(data.text, "html.parser")
    for u in soup.find_all("a"):
        pdf_url = u["href"]
        if pdf_url == "#":
            p=re.search("location\.href='.*';",str(u))
            if p!=None:
                print(p.group()[15:-2])

