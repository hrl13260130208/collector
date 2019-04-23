from bs4 import BeautifulSoup
import requests
from configparser import ConfigParser
import PyPDF2
from collector import name_manager
import faker
import logging
from collector.errors import NoConfError
import time
import copy
import urllib.parse as parse
import random
from collector import collect
import pdfminer

fake = faker.Factory.create()


logger = logging.getLogger("logger")

class config_parser():
    def __init__(self,*file_name):
        self.conf = ConfigParser()
        self.tm = name_manager.template_manager()
        self.backup_file=collect.back_file
        if file_name:
            self.file_name=file_name
        else:
            self.file_name = "conf.cfg"

    def test(self,section,url,*config):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if config:
            self.conf.read(config)
        else:
            self.conf.read(self.file_name)
        conf_test=self.conf.items(section)
        return  HTML(None,None,None).test(conf_test,url)

    def get_section(self,section):
        self.conf.read(self.file_name,encoding="utf-8")
        return self.conf.items(section)

    def paser(self):
        self.conf.read(self.file_name,encoding="utf-8")
        sections=self.conf.sections()
        for section in sections:
            rne=section.split("_")
            if rne[0]=="common":
                self.tm.save_common_conf(self.conf.items(section))
            else:
                jcb=name_manager.json_conf_bean(rne[0],rne[1])
                jcb.set_conf(self.conf.items(section))
                self.tm.save(jcb)

    def backup(self):
        file=open(self.backup_file,"w+")
        for sourcename in self.tm.get_conf_name():
            for conf in self.tm.get_eissns(sourcename):
                if not self.tm.is_default_key(conf):
                    file.write(sourcename+"#"+conf+"#"+self.tm.get_conf_string(conf)+"\n")

    def read_backup(self):
        file=open(self.backup_file)
        for line in file.readlines():
            args=line.split("#")
            jcb=name_manager.json_conf_bean(args[0],args[1])
            jcb.paser(args[2])
            self.tm.save(jcb)






class HTML():
    def __init__(self,eb,jcb,tm):
        self.eb=eb
        self.jcb=jcb
        self.tm=tm

    def run(self,url):
        if self.load(self.jcb):
            logger.info("load secuess")
            return self.do_run(self.jcb.conf,url)
        else:
            logger.info("load faild,test default confs...")
            confs=self.tm.get_default(self.jcb)
            for conf in confs:
                new_jcb=name_manager.json_conf_bean(self.jcb.get_sourcename(),self.eb.eissn)
                new_jcb.paser(conf)
                if self.test(new_jcb.conf,url):
                    logger.info("find a conf form default!")
                    self.tm.save(new_jcb)
                    return self.do_run(new_jcb.conf,url)

            logger.info("test common confs...")
            confs = self.tm.get_common_conf()
            for conf in confs:
                new_jcb = name_manager.json_conf_bean(self.jcb.get_sourcename(), self.eb.eissn)
                new_jcb.paser(conf)
                if self.test(new_jcb.conf, url):
                    logger.info("find a conf form default!")
                    self.tm.save(new_jcb)
                    return self.do_run(new_jcb.conf, url)
            logger.error("There is no conf available!")
            raise NoConfError("no conf")


    def load(self,jcb):
        string= self.tm.get(jcb)
        if string :
            jcb.paser(string)
            return True
        else:
            return False

    def test(self,conf,url):
        copy_conf=copy.deepcopy(conf)
        result=None
        try:
            result=self.do_run(copy_conf,url)
            download(result,collect.test_file)
            checkpdf(collect.test_file)
        except:
            logger.error(url+" has err: ",exc_info = True)
            result=None
        return result !=None

    def test_full_url(self,url):
        num=-1
        try:
            download(url, collect.test_file)
            num=checkpdf(collect.test_file)
        except:
            return False
        return num>0





    def do_run(self,conf,url):
        conf.sort()
        for li in conf:
            if li[0]=="type":
                if li[1]=="1":
                    conf.remove(li)
                    return self.type_1(conf,url)
                elif li[1]=="2":
                    conf.remove(li)
                    return self.type_2(conf, url)
        return self.type_default(conf,url)

    def type_1(self,conf,url):
        return type_1_parser(conf,url).run()


    def type_2(self,conf,url):
        print("_______________")

    def type_default(self,conf,url):
        # print("=++")
        return  type_default_parser(conf,url).run()
        # url_s = ""
        # url_num = 0
        # html = get_html(url)
        # soup = BeautifulSoup(html, "html.parser")
        # last = conf[conf.__len__() - 1]
        # if last[0].find("url") != -1:
        #     temp_s = last[0].split("_")
        #     if temp_s.__len__() != 1:
        #         url_num = int(temp_s[1])
        #     url_s = last[1]
        #     conf.remove(last)
        # return self.run_url(url_s, url_num, conf, soup)



    def get_url(self,string,soup):
        pass




class common_type_parser:
    def __init__(self, conf, url):
        self.conf = conf
        self.url = url

    def run(self):
        url_s = ""
        url_num = 0
        last = self.conf[self.conf.__len__() - 1]
        if last[0].find("url") != -1:
            temp_s = last[0].split("_")
            if temp_s.__len__() != 1:
                url_num = int(temp_s[1])
            url_s = last[1]
            self.conf.remove(last)
        return self.run_url(url_s, url_num,self.url)

    def run_url(self, url_s, url_num,s_url):
        first = self.conf[0]
        html,url_p = get_html(s_url)
        soup = BeautifulSoup(html, "html.parser")
        url = self.get_url(first[1], soup)
        self.conf.remove(first)
        logger.debug("url : " + url)
        if self.conf.__len__() == 0:

            if url_num == 0:
                if url_s =="default":

                    if "com" in url_p:
                        num = url_p.find(".com")
                    elif "org" in url_p:
                        num = url_p.find(".org")
                    url_s = url_p[:num + 4]
                return url_s + url
            else:
                return url
        else:
            if int(first[0]) == url_num:
                n_url=url_s + url
            else:
                n_url=url
            return self.run_url(url_s, url_num,n_url)
    def get_url(self,line,soup):
        pass


class type_1_parser(common_type_parser):

    def get_url(self,line,soup):
        strs = line.split(";")
        logger.debug("Strings split by ; is : " + str(strs))
        tag = self.find(strs, soup)
        if tag.name == "a":
            return tag["href"]

    def find(self, strs, soup):
        first_args = strs[0]
        args = first_args.split(",")
        tag=None
        if args.__len__()==4:
            tags = soup.find_all(args[0], attrs={args[1]: args[2]})
            for t in tags:
                # print(t.get_text().lower())
                if args[3].lower() in t.get_text().strip().lower():
                    tag=t
        elif args.__len__()==2:
            tags = soup.find_all(args[0])
            for t in tags:
                if args[1].lower() in  t.get_text().strip().lower() :
                    tag = t
        else:
            tag = soup.find(args[0], attrs={args[1]: args[2]})
        # logger.debug("find result: ")
        # print("______________",tag)
        strs.remove(first_args)
        if tag ==None:
            raise ValueError("tag不能为空！")
        if strs.__len__() == 0:
            return tag
        else:
            return self.find(strs, tag)




class type_default_parser(common_type_parser):
    def get_url(self,line,soup):
        strs = line.split(";")
        logger.debug("Strings split by ; is : " + str(strs))
        tag = self.find(strs, soup)
        if tag.name == "a":
            return tag["href"]
        elif tag.name == "input":
            return parse.unquote(tag["value"])
        elif tag.name == "link":
            return tag["href"]
        elif tag.name == "meta":
            return tag["content"]
        else:
            return tag.find("a")["href"]

    def find(self, strs, soup):
        first_args = strs[0]
        args = first_args.split(",")
        # print(soup)
        logger.debug("Strings split by , is : " + str(args))
        tag = soup.find(args[0], attrs={args[1]: args[2]})
        # logger.debug("find result: ")
        strs.remove(first_args)
        if strs.__len__() == 0:
            return tag
        else:
            return self.find(strs, tag)




header={"User-Agent": fake.user_agent()}

def get_html(url):
    time.sleep(random.random()*3+1)
    data = requests.get(url,headers=header,verify=False,timeout=20)
    data.encoding = 'utf-8'
    datatext = data.text
    data.close()
    return datatext,data.url

def download(url, file):
    time.sleep(random.random()*3+1)
    data = requests.get(url.strip(), headers=header,verify=False,timeout=30)
    # print(data.text)
    data.encoding = 'utf-8'
    file = open(file, "wb+")
    file.write(data.content)



def checkpdf(file):
    pdf = PyPDF2.PdfFileReader(open(file,"rb"),strict=False)
    return pdf.getNumPages()





if __name__ == '__main__':
    pdf = PyPDF2.PdfFileReader(open("C:/File/0GCoGDKpMO3X.pdf", "rb"), strict=False)
    print(pdf.getPage(2).extractText())

    # cp=config_parser()
    # res=cp.get_section("test")
    # url=HTML(None, None, None).do_run(res,"http://www.aed.org.cn/nyzyyhjxb/html/2018/2/20180205.htm")
    # print(url)

