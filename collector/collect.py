from collector import excel_rw
from collector import name_manager
from collector import threads
from collector import htmls
import os
import logging
import sys


logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger("logger")

UPDATE="update"

#文件路径配置
REPORT_PATH="F:/pdfs/report.txt"
first_dir = "F:/pdfs/"
back_file="C:/pdfs/backup"



def init_download_url_thread(um,tm,thread_list):
    url_set_names=um.get_sourcenames()
    for url_set_name in url_set_names:
        th=threads.download_url(url_set_name, um, tm)
        thread_list.append(th)
        th.start()
    return thread_list

def init_download_and_check_thread(um,thread_list,dir):
    sns=um.get_sourcenames()
    for sn in sns:
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
    thread_list = init_download_url_thread(um, tm, thread_list)
    dir = create_dir(name)
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
    url_="http://dx.doi.org/10.1016/j.ajsl.2018.12.004"
    file_="C:/File/sdf.pdf"
    section="Elsevier_1028-4559-1875-6263"
    cp=htmls.config_parser()
    cp.get_section(section)
    d_url=htmls.HTML(None,None,None).do_run(cp.get_section(section),url_)
    print(d_url)
    htmls.download(d_url,file_)
    print(htmls.checkpdf(file_))


if __name__ == '__main__':
    # name = "mc0108"
    # file_path = "F:/hrl/mc/0108/中信所待补全文清单_20190108..xls"
    #
    # # check_task(name)
    # cp=htmls.config_parser()
    # cp.paser()
    # start(name,file_path)
    # cp.backup()
    test_download()





