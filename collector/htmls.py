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
import progressbar
from collector import collect

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
        self.conf.read(self.file_name)
        return self.conf.items(section)

    def paser(self):
        self.conf.read(self.file_name)
        sections=self.conf.sections()
        for section in sections:
            rne=section.split("_")
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
            logger.info("load faild, start find a conf from default.")
            confs=self.tm.get_default(self.jcb)

            logger.debug(self.jcb.get_sourcename()+" default: "+str(confs))

            for conf in confs:
                new_jcb=name_manager.json_conf_bean(self.jcb.get_sourcename(),self.eb.eissn)
                new_jcb.paser(conf)
                if self.test(new_jcb.conf,url):
                    logger.info("find a conf form default!")

                    self.tm.save(new_jcb)
                    return self.do_run(new_jcb.conf,url)
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
        except:
            logger.error(url+" has err: ",exc_info = True)
            result=None
        return result !=None


    def do_run(self,conf,url):
        url_s=""
        url_num = 0
        html = get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        conf.sort()
        last = conf[conf.__len__() - 1]
        if last[0].find("url") != -1:
            temp_s=last[0].split("_")
            if temp_s.__len__() !=1:
                url_num=int(temp_s[1])
            url_s = last[1]
            conf.remove(last)
            # print("==========================",url_num)
            r_url=self.run_url(url_s, url_num, conf, soup)
            # print("=====================",r_url)
        return r_url

    def run_url(self,url_s,url_num,conf,soup):
        first =conf[0]
        url = self.get_url(first[1],soup)
        conf.remove(first)
        logger.debug("url : "+url)
        if conf.__len__() == 0:

            if url_num == 0:
                return url_s+url
            else:
                return url
        else:
            if int(first[0]) == url_num:
                html = get_html(url_s+url)
            else:
                html = get_html(url)
            new_soup = BeautifulSoup(html, "html.parser")
            return  self.run_url(url_s,url_num,conf,new_soup)

    def get_url(self,string,soup):
        strs=string.split(";")
        logger.debug("Strings split by ; is : "+str(strs))
        tag=self.find(strs,soup)
        if tag.name=="a":
            return tag["href"]
        elif tag.name=="input":
            return parse.unquote(tag["value"])
        else:
            return tag.find("a")["href"]

    def find(self,strs,soup):
        first_args=strs[0]
        args=first_args.split(",")
        # print(soup)
        logger.debug("Strings split by , is : "+ str(args))
        tag=soup.find(args[0],attrs={args[1]:args[2]})
        # logger.debug("find result: ")
        strs.remove(first_args)
        if strs.__len__() == 0:
            return tag
        else:
            return  self.find(strs,tag)



header={"User-Agent": fake.user_agent()}

def get_html(url):
    time.sleep(2)
    data = requests.get(url,headers=header,verify=False,timeout=20)
    data.encoding = 'utf-8'
    datatext = data.text
    data.close()
    return datatext

def download(url, file):
    time.sleep(2)
    size = 0
    data = requests.get(url, headers=header,timeout=30)
    data.encoding = 'utf-8'
    file = open(file, "wb+")
    file.write(data.content)
    # total_length = int(data.headers.get("Content-Length"))
    # with open(file, 'wb') as f:
    #     print('start download')
    #     widgets = ['Progress: ', progressbar.Percentage(), ' ', progressbar.Bar(marker='#', left='[', right=']'), ' ',
    #                progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
    #     pbar = progressbar.ProgressBar(widgets=widgets, maxval=total_length).start()
    #     for chunk in file.iter_content():
    #         if chunk:
    #             size += len(chunk)
    #             f.write(chunk)
    #         pbar.update(size)
    #     pbar.finish()
    #     f.flush()


def checkpdf(file):
    pdf = PyPDF2.PdfFileReader(file)
    return pdf.getNumPages()





if __name__ == '__main__':

    url="http://dx.doi.org/10.1007/s13753-018-0205-6"
    url2="http://dx.doi.org/10.1007/s13753-018-0199-0"
    cp=config_parser()
    # res=cp.get_section("Gruyter_2255-8683-2255-8691")
    print(cp.test("Springer_2199-6687-2199-6679",url2))
    # url="https%3A%2F%2Fasian-nursingresearch.com%2Fretrieve%2Fpii%2FS1976131718301245"
    # url=parse.unquote(url)
    # print(url)
    # print(get_html(url))


