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
import re
import os



fake = faker.Factory.create()
PROXY_POOL_URL= 'http://localhost:5555/random'

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

    # def test(self,section,url,*config):
    #     logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #     if config:
    #         self.conf.read(config)
    #     else:
    #         self.conf.read(self.file_name)
    #     conf_test=self.conf.items(section)
    #     return  HTML(None,None,None).test(conf_test,url)

    def get_section(self,section):
        self.conf.read(self.file_name,encoding="utf-8")
        return self.conf.items(section)

    def get_all_conf(self):
        self.conf.read(self.file_name, encoding="utf-8")
        items=[]
        for section in   self.conf.sections():
            items.append(self.conf.items(section))
        return items

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
    def __init__(self,eb,jcb,tm,sn,test_file=None):
        self.eb=eb
        self.jcb=jcb
        self.tm=tm
        self.sn=sn
        if test_file==None:
            self.test_file=collect.test_file
        else:
            self.test_file=test_file


    def run(self,url):
        if self.load(self.jcb):
            logger.info(self.sn+" load secuess!")
            return self.do_run(self.jcb.conf,url)
        else:
            logger.info(self.sn+" load faild,test default confs...")
            confs=self.tm.get_default(self.jcb)
            for conf in confs:
                new_jcb=name_manager.json_conf_bean(self.jcb.get_sourcename(),self.eb.eissn)
                new_jcb.paser(conf)
                if self.test(new_jcb.conf,url):
                    logger.info(self.sn+" find a conf form default!")
                    self.tm.save(new_jcb)
                    return self.do_run(new_jcb.conf,url)

            logger.info(self.sn+" test common confs...")
            confs = self.tm.get_common_conf()
            for conf in confs:
                new_jcb = name_manager.json_conf_bean(self.jcb.get_sourcename(), self.eb.eissn)
                new_jcb.paser(conf)
                if self.test(new_jcb.conf, url):
                    logger.info(self.sn+" find a conf form default!")
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
            print("-----------",result)
            download(result,self.test_file)
            checkpdf(self.test_file)
        except:
            logger.error("test run:"+url+" has err: ",exc_info = True)
            result=None
        return result !=None

    def test_full_url(self,url):
        '''
        测试full_url,是否是pdf链接
        :param url:
        :return:
        '''
        num=-1
        try:
            download(url, collect.test_file)
            num=checkpdf(collect.test_file)
        except:
            return False
        return num>0

    def do_run(self,conf,url):
        conf.sort()
        replace_1=""
        replace_2=""
        r_url=None
        for li in conf:
            if li[0] =="url_replace":
                rs=li[1].split(",")
                replace_1=rs[0]
                replace_2=rs[1]
                conf.remove(li)

        for li in conf:
            if li[0]=="type":
                if li[1]=="1":
                    conf.remove(li)
                    r_url= self.type_1(conf,url)
                elif li[1]=="2":
                    conf.remove(li)
                    r_url= self.type_2(conf, url)
        if r_url==None:
            r_url= self.type_default(conf,url)

        return r_url.replace(replace_1,replace_2)

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
        url_s =None
        url_num = None
        last = self.conf[self.conf.__len__() - 1]
        if last[0].find("url") != -1:
            temp_s = last[0].split("_")
            if temp_s.__len__() == 2:
                url_num = int(temp_s[1])
            elif temp_s.__len__() ==1:
                url_num=self.conf.__len__()-1
            url_s = last[1]
            self.conf.remove(last)

        return self.run_url(url_s, url_num,self.url)

    def run_url(self, url_s, url_num,s_url):
        first = self.conf[0]
        html,url_p = get_html(s_url)
        soup = BeautifulSoup(html, "html.parser")
        url = self.get_url(first[1], soup)
        self.conf.remove(first)

        if self.conf.__len__() == 0:
            # print("=============",self.get_new_url(first,url_num,url_s,url_p,url))
            return self.get_new_url(first,url_num,url_s,url_p,url)
        else:
            n_url=self.get_new_url(first, url_num, url_s, url_p,url)
            # print("________",n_url)
            return self.run_url(url_s, url_num,n_url)

    def get_url(self,line,soup):
        pass

    def get_new_url(self,first,url_num,url_s,url_p,url):
        '''
        根据配置文件与爬取的结果生成新的url
        :return:
        '''
        if url_num == None:
            if "http" in url:
                return url
            else:
                prefix_url = self.get_url_prefix(url_p)
                return self.merge_url(prefix_url, url)
        else:
            if int(first[0]) == url_num:
                if url_s.isdigit():
                    url_s=self.get_url_prefix_by_conf_num(url_p,int(url_s))
                return  self.merge_url(url_s,url)
            else:
                if "http" in url:
                    return url
                else:
                    prefix_url = self.get_url_prefix(url_p)
                    return self.merge_url(prefix_url, url)




    def merge_url(self,prefix_url,url):
        '''
        拼接链接
        :param prefix_url:
        :param url:
        :return:
        '''
        if prefix_url[-1] == "/" or prefix_url[-1] == "\\":
            prefix_url=prefix_url[:-1]

        if url[0] == "/" or url[0] == "\\":
            new_url = prefix_url + url
        else:
            new_url = prefix_url + "/" + url
        return  new_url

    def get_url_prefix_by_conf_num(self,url,conf_num):
        '''
        通过配置文件中url配置的数字来获取前缀
        数字表示从右向左数的‘/’的个数
        :param url:
        :param conf_num:
        :return:
        '''
        for i in range(conf_num):
            num1 = url.rfind("/")
            num2 = url.rfind("\\")
            if num1 != -1:
                if num2 != -1:
                    if num2 < num1:
                        num1 = num2
                url =url[:num1]
            else:
                if num2 != -1:
                    url = url[:num2]
        return url




    def get_url_prefix(self,url):
        '''

        :param url:
        :return:
        '''
        h_url = re.match("http.*//", url).group()
        line = url.replace(h_url, "")
        num1 = line.find("/")
        num2 = line.find("\\")
        m_url = None
        if num1 != -1:
            if num2 != -1:
                if num2 < num1:
                    num1 = num2
            m_url = line[:num1]
        else:
            if num2 != -1:
                m_url = line[:num2]
        if m_url == None:
            logger.error("获取url前缀出错，出错url："+url)
        else:
            # print(h_url + m_url)
            return h_url + m_url

class type_1_parser(common_type_parser):

    def get_url(self,line,soup):
        strs = line.split(";")
        tag = self.find(strs, soup)
        if tag.name == "a":
            # print(tag["href"])
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
                    break
        elif args.__len__()==2:
            tags = soup.find_all(args[0])
            for t in tags:
                if args[1].lower() in  t.get_text().strip().lower() :
                    tag = t
                    break
        else:
            tag = soup.find(args[0], attrs={args[1]: args[2]})
        # logger.debug("find result: ")
        # print("______________",tag)
        strs.remove(first_args)
        if tag ==None:
            raise ValueError("tag不能为空！")
        if strs.__len__() == 0:
            # print("==========",tag)
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
        elif tag.name =="object":
            return tag["data"]
        elif tag.name =="form":
            return tag["action"]
        else:
            return tag.find("a")["href"]

    def find(self, strs, soup):
        first_args = strs[0]
        args = first_args.split(",")
        # print(soup)
        # print(args)
        tag = soup.find(args[0], attrs={args[1]: args[2]})
        # logger.debug("find result: ")
        # print(tag)
        strs.remove(first_args)
        if strs.__len__() == 0:
            return tag
        else:
            return self.find(strs, tag)




#
# def get_proxy():
#     try:
#         response = requests.get(PROXY_POOL_URL)
#         if response.status_code == 200:
#             return response.text
#     except ConnectionError:
#         return None


header={"User-Agent": fake.user_agent()}


def get_html(url):
    time.sleep(random.random()*3+1)
    # print("========",url)
    data = requests.get(url,headers=header,verify=False,timeout=60)
    # print(data.cookies)
    data.encoding = 'utf-8'
    datatext = data.text
    # print(datatext)

    data.close()
    return datatext,data.url

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
        logger.warning("PDF下载出错。")
        try:
            pdffile.close()
            os.remove(file)
        except:
            logger.warning("PDF删除出错.")
        raise ValueError("PDF出错！")

#
# def get_data(url):
#     try:
#         print("======")
#         proip=find_proxy_ip()
#         return  requests.get(url, headers=header, proxies=proip,verify=False, timeout=60)
#     except:
#
#         return retry(url)

# def retry(url):
#     for i in range(5):
#         try:
#             print("+++++++=")
#             proip = find_proxy_ip()
#             return requests.get(url, headers=header, proxies=proip, verify=False, timeout=60)
#         except:
#             print("重试失败！")

# def find_proxy_ip():
#     while(True):
#         try:
#             proip = {"http": "http://" + get_proxy()}
#             data = requests.get("http://icanhazip.com", proxies=proip, headers=header, verify=False, timeout=30)
#         except:
#             print("获取ip失败！")
#             continue
#         return proip

if __name__ == '__main__':
    # pdf = PyPDF2.PdfFileReader(open("C:/File/0GCoGDKpMO3X.pdf", "rb"), strict=False)
    # print(pdf.getPage(2).extractText())
    # print(type(get_proxy()))
    url="http://hdl.handle.net/2060/19810069217"
    download(url,"C:/File/sdf55.pdf")
    # print(retry(url).text)
    # print(get_data(url).text)
    # cp=config_parser()
    # res=cp.get_section("test")
    # url=HTML(None, None, None).do_run(res,"http://www.aed.org.cn/nyzyyhjxb/html/2018/2/20180205.htm")
    # print(url)
    # h_url=re.match("http.*//",url).group()
    # line=url.replace(h_url,"")
    # num1=line.find("/")
    # num2=line.find("\\")
    # m_url=None
    # if  num1!=-1:
    #     if num2!=-1:
    #         if num2<num1:
    #             num1=num2
    #     m_url=line[:num1]
    # else:
    #     if num2!=-1:
    #         m_url=line[:num2]
    # if m_url==None:
    #     print("err")
    # else:
    #     print(h_url+m_url)

    # print(url[:-2])




