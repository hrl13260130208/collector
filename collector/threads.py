import uuid
import time
import threading
from collector import name_manager
from collector import htmls
import os
import logging
from  collector.errors import NoConfError

logger = logging.getLogger("logger")
class download_url(threading.Thread):
    def __init__(self,url_set_name,um,tm):
        threading.Thread.__init__(self)
        self.url_set_name=url_set_name
        self.sourcename=url_set_name.split("_")[1]
        self.um=um
        self.tm=tm
        self.step=1
        self.err_step=3
        self.um.save_step_names(self.sourcename,self.step)

    def run(self):
        logger.info(self.sourcename+" download_url start...")
        while(True):
            string=self.um.get_eb(self.url_set_name)
            if string ==None:
                self.um.set_done(self.sourcename,self.step)
                break
            eb=name_manager.execl_bean()
            eb.paser(string)
            url=""
            if eb.sourcename == "PMC":
                url="https://www.ncbi.nlm.nih.gov/pmc/articles/"+eb.waibuaid
            else:
                url= eb.pinjie

            jcb = name_manager.json_conf_bean(eb.sourcename, eb.eissn)
            try:
                logger.info("get download url form: "+url)
                full_url=htmls.HTML(eb,jcb,self.tm).run(url)
            except NoConfError:
                logger.info(eb.eissn+" 无可用的conf.")
                eb.err_and_step=str(self.step)+"：  无可用的conf"
                self.um.save(eb, self.err_step)
            except Exception as e:
                logger.error("download_url " + self.sourcename + " has err",exc_info = True)
                if eb.retry <5:
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
        logger.info(self.sourcename + " download_url finsh.")


class download(threading.Thread):
    def __init__(self,url_set_name,um,dir):
        threading.Thread.__init__(self)
        self.dir=dir
        self.url_set_name = url_set_name
        self.sourcename = url_set_name.split("_")[1]
        self.um=um
        self.step=2
        self.err_step = 3

    def run(self):
        logger.info(self.sourcename + " download start...")
        while(True):
            string = self.um.get_eb(self.url_set_name)
            if string == None:
                if self.um.get_done(self.sourcename,self.step-1) == self.um.DONE:
                    break
                else:
                    logger.info(self.sourcename+ " wait for download...")
                    time.sleep(30)
                    continue
            eb = name_manager.execl_bean()
            eb.paser(string)
            file_path=self.creat_filename()
            try:
                htmls.download(eb.full_url,file_path)
            except Exception :
                logger.error("download " + self.sourcename + " has err",exc_info = True)
                if eb.retry <5:
                    logger.info("retry time:" + str(eb.retry) )
                    eb.retry += 1
                    self.um.save(eb,self.step-1)
                else:
                    logger.info("retry:" + str(eb.retry) + "retry次数超过5次，不再重试。")
                    self.um.save(eb,self.err_step)
                continue

            try:
                eb.page=htmls.checkpdf(file_path)
            except Exception as e:
                logger.error(self.sourcename + "check pdf has err",exc_info = True)
                os.remove(file_path)
                if eb.retry <5:
                    logger.info("retry time:" + str(eb.retry) )
                    eb.retry += 1
                    self.um.save(eb,self.step-1)
                else:
                    logger.info("retry:" + str(eb.retry) + ".retry次数超过5次，不再重试。")
                    self.um.save(eb,self.err_step)
                continue
            eb.full_path=file_path[8:]
            self.um.save(eb,self.step)
        logger.info(self.sourcename + " download finsh.")

    def creat_filename(self):
        uid=str(uuid.uuid1())
        suid=''.join(uid.split('-'))
        return self.dir+suid+".pdf"

if __name__ == '__main__':

    pass
