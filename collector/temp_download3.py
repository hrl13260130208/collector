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

fake = faker.Factory.create()

first_dir = "C:/pdfs/"
# name="1"
name="13"
# url_file="C:/pdfs/url1.txt"
# url_file="C:/pdfs/url.txt"
redis_ = redis.Redis(host="10.3.1.99", port=6379 ,decode_responses=True)
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
        "Upgrade-Insecure-Requests": "1"
}

def checkpdf(file):
    pdf = PyPDF2.PdfFileReader(open(file,"rb"),strict=False)
    return pdf.getNumPages()

def wait():
    time.sleep(random.random() * 3+1)

def download():
    url="http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE/PROCEEDING/PROCEEDING.htm"
    data=requests.get(url)

    soup=BeautifulSoup(data.text,"html.parser")
    for a in soup.find_all("a"):
        if "home" in a.get_text().lower():
            continue
        url1="http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE/PROCEEDING/"+a["href"]
        wait()
        data_1 = requests.get(url1)
        soup = BeautifulSoup(data_1.text, "html.parser")
        for a in soup.find_all("a"):
            url2 = "http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE" + a["href"][2:]
            print(url2)
            data_2 = requests.get(url2)
            soup = BeautifulSoup(data_2.text, "html.parser")
            a = soup.find("a")
            if a != None:
                try:
                    url_2 = "http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE" + a["href"][2:]
                except:
                    for a_tags in soup.find_all("a"):
                        if "href" in a_tags:
                            url_2="http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE" + a_tags["href"][2:]
                            break

                if redis_.sadd(url_dict,url_2) == 1:
                    try:
                        file_name = creat_filename(create_dir("0410"))
                        wait()
                        pdf = requests.get(url_2, headers=header, verify=False, timeout=30)
                        pdf.encoding = 'utf-8'
                        file = open(file_name, "wb+")
                        file.write(pdf.content)
                        file.close()
                    except:
                        pass
                    try:
                        page = checkpdf(file_name)
                        if page>0:
                            print("已下载数据："+url_2+"  "+file_name)
                            redis_.lpush(finsh_name,url_2+"  "+file_name)
                            redis_.sadd(url_dict,url_2)
                    except:
                        redis_.lpush(delete_name,file_name)

    print("链接已完成，开始写数据...")
    write()


def write():
    write_file = open("C:/pdfs/list" + name + ".txt", "a+")

    while (True):
        string = redis_.lpop(finsh_name)
        if string == None:
            break
        write_file.write(string + "\n")
    while (True):
        string = redis_.lpop(delete_name)
        if string == None:
            break
        print("删除文件："+string)
        try:
            os.remove(string)
        except:
            pass

    write_file.close()



if __name__ == '__main__':
    download()
    # print(redis_.llen(delete_name))
    # print(redis_.llen(finsh_name))
    # write()
    # write_file = open("C:/pdfs/list" + name + ".txt")
    # for line in write_file.readlines():
    #
    #     path=line.split("  ")[1].replace("\n","")
    #     try:
    #         os.remove(path)
    #     except:
    #         pass

    # url2="http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE/INDEX/Index-1159.htm"
    # data_2 = requests.get(url2)
    # soup = BeautifulSoup(data_2.text, "html.parser")
    # a = soup.find("a")
    # print("href" in a)








