from collector import excel_rw
from collector import name_manager as nm
from collector import threads
from collector import htmls
import os
import logging
from concurrent.futures import ThreadPoolExecutor,as_completed
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

#关闭安全请求警告
urllib3.disable_warnings(InsecureRequestWarning)


logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger("logger")

UPDATE="update"

#文件路径配置
# REPORT_PATH="F:/pdfs/report.txt"
# back_file="F:/pdfs/backup"
# first_dir = "F:/pdfs/"

REPORT_PATH="C:/pdfs/report.txt"
first_dir = "C:/pdfs/"
back_file="C:/pdfs/backup"

test_file="C:/File/sdf.pdf"
#test_file="C:/File/sdf.pdf"

#重试次数
DOWNLOAD_URL_RETRY=5
DOWNLOAD_RETRY=5
CHECK_PDF_RETRY=3

executor=ThreadPoolExecutor(4)

def init_download_url_thread(um,tm,thread_list,dir):
    url_set_names=um.get_sourcenames()
    for url_set_name in url_set_names:
        if url_set_name == "Elsevier":
            th=threads.Elsevier_download(url_set_name,um,tm,dir)
        else:
            th=threads.download_url(url_set_name, um, tm)
        thread_list.append(th)
        th.start()
    return thread_list

def init_download_and_check_thread(um,thread_list,dir):
    sns=um.get_sourcenames()
    for sn in sns:
        if sn =="Elsevier":
            continue
        th=threads.download(sn, um, dir)
        thread_list.append(th)
        th.start()
    return thread_list

def create_dir(dir_name):
    # first_dir = "F:/pdfs/"

    dir = first_dir +dir_name + "/"
    if not os.path.exists(dir):
        if not os.path.exists(first_dir):
            os.mkdir(first_dir)
        os.mkdir(dir)
    return dir

def start(name,file_path):
    thread_list = []

    um = nm.url_manager(name)
    tm = nm.template_manager()
    execl = excel_rw.excels(file_path, um)
    execl.write()
    um.clear()
    execl.read()
    dir = create_dir(name)

    thread_list = init_download_url_thread(um, tm, thread_list,dir)
    thread_list = init_download_and_check_thread(um, thread_list, dir)

    for th in thread_list:
        th.join()

    execl.write()
    execl.report()
    um.clear()


def run_d_thread(name):
    um = nm.url_manager(name)
    tm = nm.template_manager()


def run_thread(name,file_path):
    '''
    启动方法:
        主机器启动：会读写excel
    :param name:
    :param file_path:
    :return:
    '''
    # name="test"
    # file_path="C:/temp/gruyter2018-2019待采全文的文章清单.xls"
    list = []

    um = nm.url_manager(name)
    tm = nm.template_manager()
    execl = excel_rw.excels(file_path, um)
    # delte_error_pdf(um)
    execl.write()
    um.clear()
    execl.read()
    dir = create_dir(name)

    url_set_names = um.get_sourcenames()
    for url_set_name in url_set_names:
        if url_set_name == "Elsevier":
            th = threads.Elsevier_download(url_set_name, um, tm, dir)
        elif url_set_name == "IEEE":
            th= threads.IEEE_download(url_set_name, um, tm, dir)
        # elif url_set_name == "Doaj":
        #     # pass
        #     th = threads.Single_thread(url_set_name, um, tm, dir)
        elif url_set_name=="osti":
            th=threads.OSTI(url_set_name,um,tm,dir)
        else:
            th = threads.download_url(url_set_name, um, tm,dir=first_dir)
        list.append(th)

    sns = um.get_sourcenames()
    for sn in sns:
        if sn == "Elsevier"or sn == "IEEE" or sn=="osti":
            continue

        th = threads.download(sn, um, dir)
        list.append(th)

    for t in list:
        t.start()
    for t in list:
        t.join()

    execl.write()
    execl.report()
    um.clear()


def delte_error_pdf(um):
    logger.info("删除下载错误的pdf...")
    while(True):
        err_path=um.get_error_pdf_name()
        if err_path ==None:
            break
        try:
            logger.info("pdf路径："+err_path)
            os.remove(err_path)
        except:
            pass


def check_task(name):
    um = nm.url_manager(name)
    um.query()

def check_finsh_task(name):
    um = nm.url_manager(name)
    um.query_finsh_url()

def check_conf():
    tm=nm.template_manager()
    tm.check_confs()

def test_download():
    url_="http://pubs.rsc.org/en/content/articlelanding/2019/ra/c9ra01295h"

    section="common_1"
    cp=htmls.config_parser()
    cp.get_section(section)
    d_url=htmls.HTML(None,None,None,"test").do_run(cp.get_section(section),url_)
    # d_url="https://nepis.epa.gov/Exe/ZyPDF.cgi/9101XEFB.PDF?Dockey=9101XEFB.PDF"
    # d_url="https://www.osti.gov/biblio/4646168"
    print(d_url)
    htmls.download(d_url.strip(),test_file)
    print(htmls.checkpdf(test_file))

def test_get_html():
    url="http://dx.doi.org/10.1016/j.ekir.2019.05.594"
    print(requests.get(url).text)

if __name__ == '__main__':

    # # name = "zx0815"
    # name = "test"
    # # name = "yj0329"
    # # name = "jx0122"
    #
    # # file_path = "C:/Users/zhaozhijie.CNPIEC/Desktop/temp/0329/冶金所待补全文清单_20190329..xls"
    # # file_path = "F:/hrl/mc/0121/机械所待补全文清单_20190121..xls"
    #
    # # file_path = "C:/temp/gruyter2018-2019待采全文的文章清单.xls"
    # file_path = r"C:\temp\test.xls"
    #
    # # file_path = r"C:\public\目次采全文\0815\中信所待补全文清单_20190815..xls"
    #
    # #check_task(name)
    # cp=htmls.config_parser()
    # cp.paser()
    # run_thread(name,file_path)
    # cp.backup()

    test_download()
    # test_get_html()





