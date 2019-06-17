import uuid
import time
import threading
from collector import name_manager as nm
from collector import htmls
import requests
import logging
from  collector.errors import NoConfError
from collector import collect
import re
import random
from bs4 import BeautifulSoup

logger = logging.getLogger("logger")
class download_url(threading.Thread):
    def __init__(self,sourcename,um,tm):
        threading.Thread.__init__(self)
        self.sourcename=sourcename
        self.um=um
        self.tm=tm
        self.step=1
        self.err_step=3
        self.url_set_name = um.fix(sourcename, self.step - 1)

    def run(self):
        logger.info("URL_THREAD - "+self.name+" - "+self.sourcename+" download_url start...")
        while(True):
            string=self.um.get_eb(self.url_set_name)
            if string ==None:
                self.um.set_done(self.sourcename,self.step)
                break
            eb=nm.execl_bean()
            eb.paser(string)
            url=""
            if eb.sourcename == "PMC":
                # if eb.waibuaid =="":
                #     if eb.abs_url!="":
                #         url=eb.abs_url
                #     else:
                #         url=eb.pinjie
                # else:
                #     url="https://www.ncbi.nlm.nih.gov/pmc/articles/"+eb.waibuaid
                url = eb.pinjie
            else:
                if eb.abs_url!="":
                    url=eb.abs_url
                else:
                    url= eb.pinjie


            jcb = nm.json_conf_bean(eb.sourcename, eb.eissn)
            html_=htmls.HTML(eb,jcb,self.tm)
            try:
                if eb.full_url == "":
                    logger.info("URL_THREAD - "+self.name+" - "+self.sourcename+" get download url form: "+url)
                    full_url=html_.run(url)
                else:
                    if html_.test_full_url(eb.full_url):
                        full_url=eb.full_url
                    else:
                        full_url = html_.run(eb.full_url)

            except NoConfError:
                logger.info(eb.sourcename+" "+eb.eissn+" 无可用的conf.")
                eb.err_and_step=str(self.step)+"：  无可用的conf"
                self.um.save(eb, self.err_step)
                continue
            except Exception as e:
                logger.error(self.sourcename +" download url " + url + " has err",exc_info = True)
                if eb.retry <collect.DOWNLOAD_URL_RETRY:
                    logger.info("retry time:"+str(eb.retry))
                    eb.retry += 1
                    self.um.save(eb,self.step-1)
                else:
                    logger.info("retry:" +str(eb.retry)+ ".retry次数超过5次，不再重试。")
                    eb.err_and_step = str(self.step) + "：请求下载url错误超过五次"
                    self.um.save(eb,self.err_step)
                continue

            eb.full_url = full_url
            eb.abs_url = url
            self.um.save(eb,self.step)
        logger.info("URL_THREAD - "+self.name+" - "+self.sourcename + " download_url finsh.")


class download(threading.Thread):
    def __init__(self,sourcename,um,dir):
        threading.Thread.__init__(self)
        self.dir=dir
        self.sourcename = sourcename
        self.um=um
        self.step=2
        self.err_step = 3
        self.url_set_name = um.fix(sourcename, self.step - 1)

    def run(self):
        logger.info("PDF_THREAD - "+self.name+" - "+self.sourcename + " download start...")
        while(True):
            string = self.um.get_eb(self.url_set_name)
            if string == None:
                if self.um.get_done(self.sourcename,self.step-1) == self.um.DONE:
                    self.um.set_done(self.sourcename, self.step)
                    break
                else:
                    logger.info("PDF_THREAD - "+self.name+" - "+self.sourcename+ " wait for download...")
                    time.sleep(30)
                    continue
            eb = nm.execl_bean()
            eb.paser(string)
            file_path=self.creat_filename()
            logger.info("PDF_THREAD - "+self.name+" - "+self.sourcename +" : download pdf.download url:" + eb.full_url +" 下载页面链接："+eb.pinjie )
            try:
                htmls.download(eb.full_url,file_path)
            except Exception :
                logger.error(self.sourcename +"download " + eb.full_url + " has err",exc_info = True)
                if eb.retry <collect.DOWNLOAD_RETRY:
                    logger.info("retry time:" + str(eb.retry) )
                    eb.retry += 1
                    self.um.save(eb,self.step-1)
                else:
                    logger.info("retry:" + str(eb.retry) + "retry次数超过5次，不再重试。")
                    eb.err_and_step = str(self.step) + "：下载pdf错误超过五次"
                    self.um.save(eb,self.err_step)
                continue

            logger.info("PDF_THREAD - " + self.name + " - " + self.sourcename + " :check pdf.pdf path:" +file_path)
            try:
                eb.page=htmls.checkpdf(file_path)
            except Exception as e:
                logger.error(self.sourcename + " check pdf ,pdf path: "+file_path+" has err,download url:"+eb.full_url+ " 下载页面链接：" + eb.pinjie,exc_info = True)
                # os.remove(file_path)
                self.um.save_error_pdf_name(file_path)
                if eb.retry < collect.CHECK_PDF_RETRY:
                    logger.info("retry time:" + str(eb.retry) )
                    eb.retry += 1
                    self.um.save(eb,self.step-1)
                else:
                    logger.info("retry:" + str(eb.retry) + ".retry超过指定次数，不再重试。")
                    eb.err_and_step = str(self.step) + "：pdf不完整，重下超过指定次数"
                    self.um.save(eb,self.err_step)
                continue
            eb.full_path=file_path[8:]
            self.um.save(eb,self.step)
        logger.info("URL_THREAD - "+self.name+" - "+self.sourcename + " download finsh.")

    def creat_filename(self):
        uid=str(uuid.uuid1())
        suid=''.join(uid.split('-'))
        return self.dir+suid+".pdf"

class Elsevier_download(threading.Thread):
    def __init__(self,sourcename,um,tm,dir):
        threading.Thread.__init__(self)
        self.dir=dir
        self.sourcename = sourcename
        self.um=um
        self.finsh_step=2
        self.err_step = 3
        self.tm = tm
        self.url_step = 1
        self.url_set_name = um.fix(sourcename, self.url_step - 1)

    def creat_filename(self):
        uid=str(uuid.uuid1())
        suid=''.join(uid.split('-'))
        return self.dir+suid+".pdf"

    def run(self):
        logger.info(self.sourcename + " download_url start...")
        while (True):
            string = self.um.get_eb(self.url_set_name)
            if string == None:
                break
            eb = nm.execl_bean()
            eb.paser(string)

            url = eb.pinjie

            jcb =nm.json_conf_bean(eb.sourcename, eb.eissn)
            file_path = self.creat_filename()
            html_ = htmls.HTML(eb, jcb, self.tm)
            try:
                logger.info(self.sourcename + "get download url form: " + url)
                if eb.full_url == "":
                    logger.info("URL_THREAD - "+self.name+" - "+self.sourcename+" get download url form: "+url)
                    full_url=html_.run(url)
                else:
                    if html_.test_full_url(eb.full_url):
                        full_url=eb.full_url
                    else:
                        full_url = html_.run(eb.full_url)
                # full_url = htmls.HTML(eb, jcb, self.tm).run(url)
                htmls.download(full_url, file_path)
                eb.page = htmls.checkpdf(file_path)
            except NoConfError:
                logger.info(eb.eissn + " 无可用的conf.")
                eb.err_and_step = str(self.url_step) + "：  无可用的conf"
                self.um.save(eb, self.err_step)
            except Exception as e:
                logger.error(self.sourcename + " download url " + url + " has err", exc_info=True)
                if eb.retry < collect.DOWNLOAD_URL_RETRY:
                    logger.info("retry time:" + str(eb.retry))
                    eb.retry += 1
                    self.um.save(eb, self.url_step - 1)
                else:
                    logger.info("retry:" + str(eb.retry) + ". retry次数超过5次，不再重试。")
                    self.um.save(eb, self.err_step)
                continue

            eb.full_url = full_url
            eb.abs_url = url
            eb.full_path = file_path[8:]
            self.um.save(eb, self.finsh_step)

class IEEE_download(threading.Thread):
    def __init__(self,sourcename,um,tm,dir):
        threading.Thread.__init__(self)
        self.dir=dir
        self.sourcename = sourcename
        self.um=um
        self.finsh_step=2
        self.err_step = 3
        self.tm = tm
        self.url_step = 1
        self.url_set_name = um.fix(sourcename, self.url_step - 1)

    def creat_filename(self):
        uid=str(uuid.uuid1())
        suid=''.join(uid.split('-'))
        return self.dir+suid+".pdf"

    def run(self):
        logger.info(self.sourcename + " download_url start...")
        while (True):
            string = self.um.get_eb(self.url_set_name)
            if string == None:
                break
            eb = nm.execl_bean()
            eb.paser(string)
            url = eb.pinjie
            jcb = nm.json_conf_bean(eb.sourcename, eb.eissn)
            file_path = self.creat_filename()

            try:
                d_url = self.get_d_url(url)

                # print(d_url)
                logger.info(self.sourcename + " get download url form: " + d_url)
                htmls.download(d_url, file_path)
                eb.page = htmls.checkpdf(file_path)
            except NoConfError:
                logger.info(eb.eissn + " 无可用的conf.")
                eb.err_and_step = str(self.url_step) + "：  无可用的conf"
                self.um.save(eb, self.err_step)
            except Exception as e:
                logger.error(self.sourcename + " download url " + url + " has err", exc_info=True)
                if eb.retry < collect.DOWNLOAD_URL_RETRY:
                    logger.info("retry time:" + str(eb.retry))
                    eb.retry += 1
                    self.um.save(eb, self.url_step - 1)
                else:
                    logger.info("retry:" + str(eb.retry) + ". retry次数超过5次，不再重试。")
                    self.um.save(eb, self.err_step)
                continue
            eb.full_url = d_url
            eb.abs_url = url
            eb.full_path = file_path[8:]
            self.um.save(eb, self.finsh_step)


    def get_d_url(self,url):
        time.sleep(random.random()*3+1)
        data = requests.get(url)
        lines = re.search("\"pdfUrl\":\".*\",", data.text).group()
        for l in lines.split(","):
            args = l.split(":")
            if args.__len__() == 2:
                if args[0].find("pdfUrl") != -1:
                    n_url="https://ieeexplore.ieee.org"+args[1][1:-1]
                    time.sleep(random.random() * 3 + 1)
                    n_data = requests.get(n_url)
                    soup = BeautifulSoup(n_data.text, "html.parser")
                    iframe = soup.find("iframe")
                    return iframe["src"]

class Single_thread(threading.Thread):
    def __init__(self,sourcename,um,tm,dir):
        threading.Thread.__init__(self)
        self.dir=dir
        self.sourcename = sourcename
        self.um=um
        self.finsh_step=2
        self.err_step = 3
        self.tm = tm
        self.url_step = 1
        self.url_set_name = um.fix(sourcename, self.url_step - 1)

    def creat_filename(self):
        uid=str(uuid.uuid1())
        suid=''.join(uid.split('-'))
        return self.dir+suid+".pdf"

    def run(self):
        logger.info(self.sourcename + " download_url start...")
        while (True):
            string = self.um.get_eb(self.url_set_name)
            if string == None:
                break
            eb = nm.execl_bean()
            eb.paser(string)
            url = ""
            if eb.sourcename == "PMC":
                url = "https://www.ncbi.nlm.nih.gov/pmc/articles/" + eb.waibuaid
            else:
                url = eb.pinjie

            jcb =nm.json_conf_bean(eb.sourcename, eb.eissn)
            file_path = self.creat_filename()
            try:
                html_=htmls.HTML(eb,jcb,self.tm)
                if eb.full_url == "":
                    # logger.info("URL_THREAD - "+self.name+" - "+self.sourcename+" get download url form: "+url)
                    print("+++++++++++++++++")
                    print(eb.full_url)
                    full_url=html_.run(url)
                else:
                    print("=====================",eb.full_url)
                    if html_.test_full_url(eb.full_url):
                        full_url=eb.full_url
                    else:
                        full_url = html_.run(eb.full_url)
                print("下载pdf...",full_url)
                htmls.download(full_url, file_path)
                eb.page = htmls.checkpdf(file_path)
                print("下载成功")
            except NoConfError:
                logger.info(eb.eissn + " 无可用的conf.")
                eb.err_and_step = str(self.url_step) + "：  无可用的conf"
                self.um.save(eb, self.err_step)
            except Exception as e:
                logger.error(self.sourcename + " download url " + url + " has err", exc_info=True)
                if eb.retry < collect.DOWNLOAD_URL_RETRY:
                    logger.info("retry time:" + str(eb.retry))
                    eb.retry += 1
                    self.um.save(eb, self.url_step - 1)
                else:
                    logger.info("retry:" + str(eb.retry) + ". retry次数超过5次，不再重试。")
                    self.um.save(eb, self.err_step)
                continue

            eb.full_url = full_url
            eb.abs_url = url
            eb.full_path = file_path[8:]
            self.um.save(eb, self.finsh_step)


if __name__ == '__main__':

    pass

    # url="https://ieeexplore.ieee.org/document/8353939/"
    # data = requests.get(url)
    # lines = re.search("\"pdfUrl\":\".*\",", data.text).group()
    # for l in lines.split(","):
    #     args = l.split(":")
    #     if args.__len__() == 2:
    #         if args[0].find("pdfUrl") != -1:
    #             n_url = "https://ieeexplore.ieee.org" + args[1][1:-1]
    #             time.sleep(random.random() * 3 + 1)
    #             n_data = requests.get(n_url)
    #             soup=BeautifulSoup(n_data.text,"html.parser")
    #             iframe=soup.find("iframe")
    #             print(iframe["src"])

