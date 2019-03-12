from collector import excel_rw
from collector import name_manager
from collector import threads
from collector import htmls
import os
import logging
import requests


logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger("logger")

UPDATE="update"

#文件路径配置
REPORT_PATH="F:/pdfs/report.txt"
# REPORT_PATH="C:/pdfs/report.txt"
first_dir = "F:/pdfs/"
# first_dir = "C:/pdfs/"
back_file="F:/pdfs/backup"
# back_file="C:/pdfs/backup"

test_file="C:/File/sdf.pdf"
#test_file="C:/File/sdf.pdf"

#重试次数
DOWNLOAD_URL_RETRY=5
DOWNLOAD_RETRY=5
CHECK_PDF_RETRY=3



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

    um = name_manager.url_manager(name)
    tm = name_manager.template_manager()
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

def check_task(name):
    um = name_manager.url_manager(name)
    um.query()

def check_finsh_task(name):
    um = name_manager.url_manager(name)
    um.query_finsh_url()

def check_conf():
    tm=name_manager.template_manager()
    tm.check_confs()

def test_download():
    url_="http://journals.tubitak.gov.tr/elektrik/abstract.htm?id=23581"

    section="Scientific and Technical Research Council of Turkey_1300-0632-1303-6203"
    cp=htmls.config_parser()
    cp.get_section(section)
    d_url=htmls.HTML(None,None,None).do_run(cp.get_section(section),url_)
    print(d_url)
    htmls.download(d_url,test_file)
    print(htmls.checkpdf(test_file))


if __name__ == '__main__':
    # name = "zx0122"
    # #name = "yj0122"
    # # name = "jx0122"
    #
    # #file_path = "F:/hrl/mc/0121/冶金所待补全文清单_20190121..xls"
    # # file_path = "F:/hrl/mc/0121/机械所待补全文清单_20190121..xls"
    # file_path = "F:/hrl/mc/0121/中信所待补全文清单_20190121..xls"
    #
    # #check_task(name)
    # cp=htmls.config_parser()
    # cp.paser()
    # start(name,file_path)
    # cp.backup()
    # url = "http://journals.tubitak.gov.tr/elektrik/issues/elk-18-26-6/elk-26-6-2-1802-189.pdf"
    # data=requests.get(url)
    # print(data.text)
    # file = open(test_file, "wb+")
    # file.write(data.content)
    test_download()






