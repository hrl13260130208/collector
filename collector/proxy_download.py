
from selenium import webdriver  # 启动浏览器需要用到
from selenium.webdriver.chrome.options import Options
import time
from browsermobproxy import Server
import requests
import os
import PyPDF2
import faker
import uuid
import traceback


server = Server(r'C:\File\tools\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat')
server.start()
proxy = server.create_proxy()

chrome_options = Options()
chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
driver_path = r"C:\File\tools\webdriver\chromedriver.exe"
driver = webdriver.Chrome(driver_path, chrome_options=chrome_options)

fake = faker.Factory.create()
header={"User-Agent": fake.user_agent()}

def drivertest(dir=r"C:\pdfs\osti_weliy"):
    # driver = webdriver.Chrome()
    writer=open(r"C:\temp\r_wiley.txt","w+",encoding="utf-8")
    with open(r"C:\temp\wiley.txt",encoding="utf-8") as f:
        for line in f.readlines():
            try:
                url=line.replace("\n","")
                # url="https://onlinelibrary.wiley.com/resolve/doi?DOI=10.1111/gcbb.12366"
                proxy.new_har("douyin", options={'captureHeaders': True, 'captureContent': True})

                driver.get(url)
                a = driver.find_element_by_link_text("PDF")
                pdfurl=a.get_attribute("href")
                if "/pdf/" in pdfurl:
                    pdfurl=pdfurl.replace("/pdf/","/epdf/")

                driver.implicitly_wait(60)
                driver.get(pdfurl)
                time.sleep(20)
                try:
                    co=driver.find_element_by_link_text("Check out")
                    writer.write(url+"##"+pdfurl+"##No pdf##-1\n")
                    continue
                except:
                    print("没有check out！")
                    pass


                result = proxy.har

                for entry in result['log']['entries']:
                    _url = entry['request']['url']
                    if "https://dyz6l42c0kkca.cloudfront.net/" in _url:
                        print(_url)
                        try:
                            file=creat_filename(dir)
                            download(_url,file)
                            num=checkpdf(file)
                            writer.write(url+"##"+pdfurl+"##"+file+"##"+str(num)+"\n")
                            break
                        except:
                            traceback.print_exc()
                            print("下载出错！")
            except:
                # print()
                traceback.print_exc()


    server.stop()
    driver.close()  # 关闭浏览器一个Tab


def download(url, file):
    # time.sleep(random.random()*3+1)
    # proip =find_proxy_ip()
    # print(url)
    # header={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    #         "Cookie": "BIGipServerlbapp_tc3=3892314634.49300.0000; BIGipServerwww.osti.gov_pool=1132494278.20480.0000; __utma=249692800.1749221367.1564467097.1564467097.1564467097.1; __utmc=249692800; __utmz=249692800.1564467097.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.1749221367.1564467097; _gid=GA1.2.298248318.1564467099; JSESSIONID=1C4287BE446C33FB1B52F566B0983D04; __utmb=249692800.57.10.1564467097"}
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

def elsevierdownload(dir="",read_path=r"C:\temp\wiley.txt",write_path=r"C:\temp\r_wiley.txt"):
    # driver = webdriver.Chrome(driver_path)
    writer = open(write_path, "w+", encoding="utf-8")
    with open(read_path, encoding="utf-8") as f:
        for line in f.readlines():
            try:
                url=line.replace("\n","")
                print(url)
                driver.switch_to.window(driver.window_handles[0])
                driver.get(url)
                a = driver.find_element_by_link_text("PDF")
                a.click()
                time.sleep(1)
                print(driver.window_handles)
                driver.switch_to.window(driver.window_handles[1])
                _url=driver.current_url
                print(_url)
                driver.close()
                try:
                    file = creat_filename(dir)
                    download(_url, file)
                    num = checkpdf(file)
                    writer.write(url + "##" + _url + "##" + file + "##" + str(num) + "\n")
                except:
                    traceback.print_exc()
                    print("下载出错！")
            except:
                traceback.print_exc()



if __name__ == '__main__':

    drivertest(dir=r"C:\pdfs\osti_weliy")
    # elsevierdownload(dir=r"C:\pdfs\yj1209",read_path=r"C:\temp\er.txt",write_path=r"C:\temp\ew.txt")






