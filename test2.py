
import requests
from bs4 import BeautifulSoup
import redis
import os
import time
import uuid
import PyPDF2

import traceback


redis_ = redis.Redis(host="10.3.1.99", port=6379, db=10,decode_responses=True)
web="web_"
url_list_name="list"
dir="C:\pdfs\osti_test"

def update(file3 = r"C:\temp\新建文件夹\todo.txt"):
    print("上传数据...")

    file = open(file3, "r", encoding="utf-8")

    for line in file.readlines():
        url=line.replace("\n","")
        redis_.lpush(url_list_name,url)

def run():
    while(redis_.llen(url_list_name)>0):
        url=redis_.lpop(url_list_name)
        print("处理链接："+url)
        try:
            s = requests.session()
            r = s.get(url,verify=False)
            try:
                c1 = s.cookies['BIGipServerlbapp_tc3']
                c2 = s.cookies['BIGipServerwww.osti.gov_pool']
                c3 = s.cookies['JSESSIONID']
            except:
                pass
            soup = BeautifulSoup(r.text, "html.parser")

            mate = soup.find("meta", {"name": "citation_pdf_url"})
            if mate == None:
                print("没有citation_pdf_url...")
                for div1 in soup.find_all("div", class_="biblio-secondary-group"):
                    for div2 in div1.find_all("div", class_="biblio-secondary-item small"):
                        for a in div2.find_all("a"):
                            if "href" in a.attrs.keys():
                                if "https://doi.org" in a["href"]:
                                    pdf_url = a["href"]
                                    data = requests.get(pdf_url)
                                    new_url = data.url
                                    # print("===========",new_url)
                                    new_url = new_url.replace("https://", "")
                                    new_url = new_url[:new_url.find("/")]
                                    redis_.lpush(web + new_url, url + "##" + data.url)
            else:
                print("找到citation_pdf_url...")
                pdf_url = mate["content"]
                # print(c1, c2, c3)
                cookies = {
                    'BIGipServerlbapp_tc3': c1,
                    'BIGipServerwww.osti.gov_pool': c2,
                    'JSESSIONID': c3,
                    '__utma': '249692800.1749221367.1564467097.1564467097.1564467097.1',
                    '__utmc': '249692800',
                    '__utmz': '249692800.1564467097.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
                    '_ga': 'GA1.2.1749221367.1564467097',
                    '_gid': 'GA1.2.298248318.1564467099',
                    '__utmt': '1',
                    '__utmb': '249692800.63.10.1564467097'
                }

                r2 = requests.get(pdf_url, cookies=cookies)
                new_url = r2.url
                new_url = new_url.replace("https://", "")
                new_url = new_url[:new_url.find("/")]
                file = creat_filename(dir)
                file = open(file, "wb+")
                file.write(r2.content)
                try:
                    num = checkpdf(file)
                    print("---------", pdf_url, new_url)
                    redis_.lpush(web + new_url, url + "##" + r2.url + "##" + file)
                except:
                    redis_.lpush(web + new_url, url + "##" + r2.url + "##$$")

                # (web + new_url, url + "##" + mate["content"])
        except:
            traceback.print_exc()
            redis_.lpush(web +"err", url )
            time.sleep(10)


def write(dir=r"C:\temp\新建文件夹"):
    print("写入文件...")
    for key in redis_.keys(web+"*"):
        path=os.path.join(dir,key+".txt")
        f=open(path,"a+",encoding="utf-8")
        for i in range(redis_.llen(key)):
            f.write(redis_.lindex(key,i)+"\n")




def test():
    url="https://www.osti.gov/biblio/6038718"
    # r = requests.get(url)
    s = requests.session()
    r=s.get(url,verify=False)
    # c1=None
    # c2=None
    # c3=None
    print(r)
    # print( s.cookies['BIGipServerlbapp_tc3'])
    # print(r.cookies.get_dict())
    c1 = s.cookies['BIGipServerlbapp_tc3']
    c2 = s.cookies['BIGipServerwww.osti.gov_pool']
    c3 = s.cookies['JSESSIONID']

    soup = BeautifulSoup(r.text, "html.parser")

    mate = soup.find("meta", {"name": "citation_pdf_url"})
    if mate == None:
        print("没有citation_pdf_url...")
        for div1 in soup.find_all("div", class_="biblio-secondary-group"):
            for div2 in div1.find_all("div", class_="biblio-secondary-item small"):
                for a in div2.find_all("a"):
                    if "href" in a.attrs.keys():
                        if "https://doi.org" in a["href"]:
                            pdf_url = a["href"]
                            data = requests.get(pdf_url)
                            new_url = data.url
                            # print("===========",new_url)
                            new_url = new_url.replace("https://", "")
                            new_url = new_url[:new_url.find("/")]
                            print(web + new_url, url + "##" + data.url)
    else:
        print("找到citation_pdf_url...")
        pdf_url=mate["content"]
        print(c1,c2,c3)
        cookies = {
            'BIGipServerlbapp_tc3': c1,
            'BIGipServerwww.osti.gov_pool': c2,
            'JSESSIONID': c3,
            '__utma': '249692800.1749221367.1564467097.1564467097.1564467097.1',
            '__utmc': '249692800',
            '__utmz': '249692800.1564467097.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
            '_ga': 'GA1.2.1749221367.1564467097',
            '_gid': 'GA1.2.298248318.1564467099',
            '__utmt': '1',
            '__utmb': '249692800.63.10.1564467097'
        }

        r2 = requests.get(pdf_url, cookies=cookies)
        new_url=r2.url
        new_url = new_url.replace("https://", "")
        new_url = new_url[:new_url.find("/")]
        file=creat_filename(dir)
        file = open(file, "wb+")
        file.write(r2.content)
        try:
            num=checkpdf(file)
            print("---------",pdf_url,new_url)
            print(web + new_url, url + "##" + r2.url+"##"+file)
        except:
            print(web + new_url, url + "##" + r2.url+"##$$")



def test2():
    r=open(r"C:\temp\osti\r1119\osti\web_www.osti.gov.txt",encoding="utf-8")
    w=open(r"C:\temp\osti\r1119\osti\do.txt","w+",encoding="utf-8")
    for line in r.readlines():
        i=line.split("##")
        w.write(i[0]+"\n")
#
# def download(url, file):
#     # time.sleep(random.random()*3+1)
#     # proip =find_proxy_ip()
#     # print(url)
#     # header={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
#     #         "Cookie": "BIGipServerlbapp_tc3=3892314634.49300.0000; BIGipServerwww.osti.gov_pool=1132494278.20480.0000; __utma=249692800.1749221367.1564467097.1564467097.1564467097.1; __utmc=249692800; __utmz=249692800.1564467097.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.1749221367.1564467097; _gid=GA1.2.298248318.1564467099; JSESSIONID=1C4287BE446C33FB1B52F566B0983D04; __utmb=249692800.57.10.1564467097"}
#     data = requests.get(url.strip(),headers=header,verify=False,timeout=30)
#     # print(data.cookies)
#     # print(data.text)
#     data.encoding = 'utf-8'
#     file = open(file, "wb+")
#     file.write(data.content)

def checkpdf(file):

    try:
        pdffile = open(file, "rb+")
        pdf = PyPDF2.PdfFileReader(pdffile, strict=False)
        num=pdf.getNumPages()
        pdffile.close()
        return num
    except:
        print("PDF下载出错。")
        try:
            pdffile.close()
            os.remove(file)
        except:
            print("PDF删除出错.")
        raise ValueError("PDF出错！")

def creat_filename(dir):
    uid=str(uuid.uuid1())
    suid=''.join(uid.split('-'))
    return os.path.join(dir,suid+".pdf")
if __name__ == '__main__':
    # for key in redis_.keys("web_*"):
    #     # redis_.delete(key)
    #     # print(key ,redis_.type(key))
    #     if redis_.type(key) == "string":
    #         print(key, redis_.get(key))
    #     elif redis_.type(key) == "set":
    #         print(key, " : ", redis_.scard(key), " : ", redis_.smembers(key))
    #     elif redis_.type(key) == "list":
    #         print(key, " : ", redis_.llen(key), " : ")  # , redis_.lrange(key,0,100))
    # test2()
    # update(file3=r"C:\temp\osti\r1119\osti\do.txt")
    run()
    write()
    # test()



