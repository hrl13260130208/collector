

from selenium import webdriver
from bs4 import BeautifulSoup
import traceback
import requests
import PyPDF2
import os
import uuid
import time

driver_path = r"C:\File\tools\webdriver\chromedriver.exe"
driver = webdriver.Chrome(driver_path)




def download(url, file):
    # time.sleep(random.random()*3+1)
    # proip =find_proxy_ip()
    # print(url)
    header={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}

    data = requests.get(url.strip(),headers=header,verify=False,timeout=30)
    # print(data.cookies)
    # print(data.text)
    data.encoding = 'utf-8'
    file = open(file, "wb+")
    file.write(data.content)

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

    path=r"C:\temp\ieee.txt"
    writer=open(r"C:\temp\ieee_w.txt","w+",encoding="utf-8")
    dir=r"C:\pdfs\osti_o2"
    f=open(path,encoding="utf-8")
    for url in f.readlines():
        time.sleep(5)
        try:
            url=url.replace("\n","")
            driver.get(url)
            a=driver.find_element_by_class_name("doc-actions-link")
            a.click()
            soup=BeautifulSoup(driver.page_source,"html.parser")
            # print(soup)
            iframe=soup.find_all("iframe")

            for item in iframe:
                try:

                    pdf_url=item["src"]
                except:
                    pass
            print(pdf_url)
            try:
                file = creat_filename(dir)
                download(pdf_url, file)
                num = checkpdf(file)
                writer.write(url + "##" + pdf_url+ "##" + file + "##" + str(num) + "\n")
            except:
                traceback.print_exc()
                print("下载出错！")
        except:
            traceback.print_exc()

    driver.close()