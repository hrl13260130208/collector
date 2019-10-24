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

class EXCEL_ITEM:
    SOURCENAME="SOURCENAME"
    ISSN="ISSN"
    EISSN="EISSN"
    WAIBUAID="WAIBUAID"
    PINJIE="PINJIE"
    FULL_URL="FULL_URL"
    ABS_URL="ABS_URL"
    FULL_PATH="FULL_PATH"

logger = logging.getLogger("logger")
class download_url(threading.Thread):
    def __init__(self,sourcename,um,tm,dir=r"c:/pdfs/"):
        threading.Thread.__init__(self)
        self.dir=dir
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
            url_dict={}
            if eb.sourcename == "PMC":
                if eb.waibuaid!="":
                    url_dict[EXCEL_ITEM.WAIBUAID]="https://www.ncbi.nlm.nih.gov/pmc/articles/"+eb.waibuaid
            if eb.abs_url!="":
                url_dict[EXCEL_ITEM.ABS_URL]=eb.abs_url
            if eb.full_url!="":
                url_dict[EXCEL_ITEM.FULL_URL]=eb.full_url
            if eb.pinjie!="":
                url_dict[EXCEL_ITEM.PINJIE]=eb.pinjie

            jcb = nm.json_conf_bean(eb.sourcename, eb.eissn)
            html_=htmls.HTML(eb,jcb,self.tm,self.sourcename,test_file=self.create_test_file_path())
            try:
                logger.info("URL_THREAD - " + self.name + " - " + self.sourcename + " get download url form: " + str(url_dict))
                url,full_url=parser_url(url_dict,html_,name=self.name + " - " + self.sourcename)
            except :
                logger.error(self.sourcename +" download url has err！url列表："+str(url_dict),exc_info = True)
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
            # eb.full_url = eb.pinjie
            # eb.abs_url = eb.pinjie
            self.um.save(eb,self.step)
        logger.info("URL_THREAD - "+self.name+" - "+self.sourcename + " download_url finsh.")
    def create_test_file_path(self):
        return self.dir+self.name+"_"+self.sourcename+".pdf"

def parser_url(url_dict,html_,name=" "):
    '''
    解析urls
    :param url_dict:
    :param html_:
    :return:
    '''
    for key in url_dict.keys():
        try:
            if html_.test_full_url(url_dict[key]):
                return url_dict[key], url_dict[key]
            else:
                return url_dict[key],html_.run(url_dict[key])
        except:
            logger.warning(name+" "+key+" 下载出错，尝试其他url...")

    raise ValueError("无法解析出PDF的url！")

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

            try:
                logger.info(
                    "PDF_THREAD - " + self.name + " - " + self.sourcename + " : download pdf.download url:" + eb.full_url + " 下载页面链接：" + eb.pinjie)
                htmls.download(eb.full_url,file_path)
                logger.info(
                    "PDF_THREAD - " + self.name + " - " + self.sourcename + " :check pdf. pdf path:" + file_path)
                eb.page = htmls.checkpdf(file_path)
            except Exception :
                logger.error(self.sourcename +" download " + eb.full_url + " has err",exc_info = True)
                if eb.retry <collect.DOWNLOAD_RETRY:
                    logger.info("retry time:" + str(eb.retry) )
                    eb.retry += 1
                    self.um.save(eb,self.step-1)
                else:
                    logger.info("retry:" + str(eb.retry) + "retry次数超过5次，不再重试。")
                    eb.err_and_step = str(self.step) + "：下载pdf错误超过五次"
                    self.um.save(eb,self.err_step)
                continue

            logger.info( "PDF_THREAD - " + self.name + " - " + self.sourcename + " :pdf下载成功。")
            dirs = file_path.split("/")
            eb.full_path = dirs[-2] + "/" + dirs[-1]
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
        logger.info(self.sourcename + " start...")
        while (True):
            string = self.um.get_eb(self.url_set_name)
            if string == None:
                break

            file_path = self.creat_filename()
            eb = nm.execl_bean()
            eb.paser(string)
            url_dict = {}

            if eb.abs_url != "":
                url_dict[EXCEL_ITEM.ABS_URL] = eb.abs_url
            if eb.full_url != "":
                url_dict[EXCEL_ITEM.FULL_URL] = eb.full_url
            if eb.pinjie != "":
                url_dict[EXCEL_ITEM.PINJIE] = eb.pinjie

            jcb = nm.json_conf_bean(eb.sourcename, eb.eissn)
            html_ = htmls.HTML(eb, jcb, self.tm, self.sourcename)
            try:
                logger.info(
                    "URL_THREAD - " + self.name + " - " + self.sourcename + " get download url form: " + str(url_dict))
                url, full_url = parser_url(url_dict, html_)
                htmls.download(full_url, file_path)
                eb.page = htmls.checkpdf(file_path)
            except NoConfError:
                logger.info(self.sourcename +"-"+eb.eissn + " 无可用的conf.")
                continue
            except Exception as e:
                logger.error(self.sourcename + " download url " + str(url_dict) + " has err", exc_info=True)
                if eb.retry < collect.DOWNLOAD_URL_RETRY:
                    logger.info("retry time:" + str(eb.retry))
                    eb.retry += 1
                    self.um.save(eb, self.url_step - 1)
                else:
                    logger.info("retry:" + str(eb.retry) + ". retry次数超过5次，不再重试。")
                    self.um.save(eb, self.err_step)
                continue

            logger.info("URL_THREAD - "+self.name+" - "+self.sourcename+" 下载成功！")
            eb.full_url = full_url
            eb.abs_url = url

            dirs = file_path.split("/")
            eb.full_path = dirs[-2] + "/" + dirs[-1]
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
            dirs = file_path.split("/")
            eb.full_path = dirs[-2] + "/" + dirs[-1]
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
                html_=htmls.HTML(eb,jcb,self.tm,self.sourcename)
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
            dirs = file_path.split("/")
            eb.full_path = dirs[-2] + "/" + dirs[-1]
            self.um.save(eb, self.finsh_step)


class OSTI(threading.Thread):
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
            try:
                # time.sleep(random.random() * 3 + 1)
                logger.info(self.sourcename+" 开始下载："+url)

                r = requests.get(url)
                try:
                    c1 = r.cookies['BIGipServerlbapp_tc3']
                    c2 = r.cookies['BIGipServerwww.osti.gov_pool']
                    c3 = r.cookies['JSESSIONID']
                except:
                    pass
                soup = BeautifulSoup(r.text, "html.parser")

                mate = soup.find("meta", {"name": "citation_pdf_url"})
                if mate == None:
                    start_break = False
                    for div1 in soup.find_all("div", class_="biblio-secondary-group"):
                        for div2 in div1.find_all("div", class_="biblio-secondary-item small"):
                            for a in div2.find_all("a"):
                                if "href" in a.attrs.keys():
                                    if "https://doi.org" in a["href"]:
                                        pdf_url = a["href"]
                                        cp = htmls.config_parser()
                                        ht = htmls.HTML(None, None, None, None)
                                        for conf in cp.get_all_conf():
                                            print(conf)
                                            if ht.test(conf, pdf_url):
                                                result = ht.do_run(conf, pdf_url)
                                                r2 = requests.get(result)
                                                r2.encoding = 'utf-8'
                                                # print(r2.text)
                                                file = open(file_path, "wb+")
                                                file.write(r2.content)
                                                file.close()
                                                break

                                        start_break = True
                                        break
                            if start_break:
                                break
                        if start_break:
                            break

                else:
                    pdf_url = mate["content"]
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
                    r2.encoding = 'utf-8'
                    # print(r2.text)
                    file = open(file_path, "wb+")
                    file.write(r2.content)
                    file.close()
                eb.page = htmls.checkpdf(file_path)
                full_url=pdf_url
                # r = requests.get(url)
                # c1 = r.cookies['BIGipServerlbapp_tc3']
                # c2 = r.cookies['BIGipServerwww.osti.gov_pool']
                # c3 = r.cookies['JSESSIONID']
                # soup = BeautifulSoup(r.text, "html.parser")
                #
                # pdf_url = soup.find("meta", {"name": "citation_pdf_url"})["content"]
                # cookies = {
                #     'BIGipServerlbapp_tc3': c1,
                #     'BIGipServerwww.osti.gov_pool': c2,
                #     'JSESSIONID': c3,
                #     '__utma': '249692800.1749221367.1564467097.1564467097.1564467097.1',
                #     '__utmc': '249692800',
                #     '__utmz': '249692800.1564467097.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
                #     '_ga': 'GA1.2.1749221367.1564467097',
                #     '_gid': 'GA1.2.298248318.1564467099',
                #     '__utmt': '1',
                #     '__utmb': '249692800.63.10.1564467097'
                # }
                # #time.sleep(random.random() * 3 + 1)
                # logger.info(self.sourcename+" 下载PDF："+pdf_url)
                #
                # r2 = requests.get(pdf_url, cookies=cookies)
                # r2.encoding = 'utf-8'
                # file = open(file_path, "wb+")
                # file.write(r2.content)
                # file.close()
                # eb.page = htmls.checkpdf(file_path)
                # full_url=pdf_url

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
            dirs = file_path.split("/")
            eb.full_path = dirs[-2] + "/" + dirs[-1]
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

