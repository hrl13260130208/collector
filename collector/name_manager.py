
import redis
import json
from collector import collect

# redis_ = redis.Redis(host="127.0.0.1", port=6379, db=1,decode_responses=True)
redis_ = redis.Redis(host="10.3.1.99", port=6379, decode_responses=True)

class conf_bean():
    def __init__(self,sourcename,eissn):
        self.sourcename=sourcename
        self.eissn=eissn

    def get_sourcename(self):
        return self.sourcename

    def get_eissn(self):
        return self.eissn

    def to_string(self):
        pass

    def paser(self,str):
        pass

    def default_name(self):
        return self.get_sourcename()+"_default"



class template_manager():
    def __init__(self):
        self.conf_name="sourcenames"

    def save(self,conf_bean):
        if not redis_.exists(conf_bean.get_sourcename()):
            redis_.sadd(self.conf_name,conf_bean.get_sourcename())
            redis_.sadd(conf_bean.get_sourcename(),conf_bean.default_name())

        redis_.sadd(conf_bean.get_sourcename(),conf_bean.get_eissn())
        redis_.set(conf_bean.get_eissn(),conf_bean.to_string())
        redis_.sadd(conf_bean.default_name(),conf_bean.to_string())

    def get(self,conf_bean):
        return redis_.get(conf_bean.get_eissn())

    def get_default(self,conf_bean):
        return redis_.smembers(conf_bean.default_name())

    def get_conf_name(self):
        return redis_.smembers(self.conf_name)

    def get_eissns(self,sourcename):
        return redis_.smembers(sourcename)

    def is_default_key(self,key):
        '''

        :param key:
        :return:
        '''
        return redis_.type(key) == "set"

    def get_conf_string(self,key):
        return redis_.get(key)

    def check_confs(self):
        for sn in redis_.smembers(self.conf_name):
            print("sourcename : ",sn)
            for conf_name in redis_.smembers(sn):
                if redis_.type(conf_name) == "set":
                    print("    ",conf_name," : ",redis_.smembers(conf_name))
                else:
                    print("    ",conf_name," : ",redis_.get(conf_name))


class json_conf_bean(conf_bean):
    def set_conf(self,conf):
        self.conf =conf


    def get_conf(self):
        return self.conf

    def to_string(self):
        return json.dumps(self.conf)

    def paser(self,str):
        self.conf=json.loads(str)


class execl_bean():
    def __init__(self):
        self.row_num=0
        self.sourcename=""
        self.eissn=""
        self.waibuaid=""
        self.pinjie=""
        self.full_url=""
        self.abs_url=""
        self.full_path=""
        self.retry=0
        self.page=-1
        self.err_and_step=""
        self.done=False

    def check(self):

        if self.full_path == "No pdf":
            self.done = True
        if self.sourcename.find("Sage")!=-1:
            self.sourcename="Sage"
        if self.sourcename.find("SRP") != -1:
            self.sourcename = "SRP"
        # print(self.sourcename.find("Sage"))
        # if self.sourcename=="Elsevier":
        #     self.done = True


    def is_done(self):
        if self.done:
            return self.done
        else:
            return self.full_url !="" and self.abs_url != "" and self.full_path != "" and self.page !=-1

    def to_string(self):
        if self.row_num == 0:
            raise ValueError("row_num 不能为 0！")
        if self.sourcename == "":
            raise ValueError("sourcename不能为空！")
        if self.eissn == "":
            raise ValueError("eissn不能为空！")
        if self.pinjie == "" and self.waibuaid =="":
            raise ValueError("pinjie与waibuaid不能为空！")
        return str(self.row_num)+"#"+self.sourcename+"#"+self.eissn+"#"+self.waibuaid+"#" \
                +self.pinjie+"#"+self.full_url+"#"+self.abs_url+"#"+self.full_path+"#"\
               +str(self.retry)+"#"+str(self.page)+"#"+self.err_and_step

    def paser(self,str):
        args=str.split("#")
        self.row_num = int(args[0])
        self.sourcename = args[1]
        self.eissn =args[2]
        self.waibuaid = args[3]
        self.pinjie = args[4]
        self.full_url = args[5]
        self.abs_url = args[6]
        self.full_path = args[7]
        self.retry=int(args[8])
        self.page = int(args[9])
        self.err_and_step=args[10]

class url_manager():
    def __init__(self,name):
        self.name=name
        self.DONE="True"

    def save_sourcenames(self,sourcename):
        redis_.sadd(self.name, sourcename)

    def save(self,execl_bean,step):
        redis_.lpush(self.fix(execl_bean.sourcename,step),execl_bean.to_string())

    def fix(self,string,step):
        return self.name+"_"+string+"_"+str(step)

    def done_name(self,sourcename,step):
        return self.name+ "_" + sourcename+ "_" + str(step)+"_done"

    def get_sourcenames(self):
        return redis_.smembers(self.name)

    def get_eb(self,sourcename):
        # print(sourcename+":",redis_.llen(sourcename))
        return redis_.rpop(sourcename)

    def set_done(self,sourcename,step):
        redis_.set(self.done_name(sourcename,step),self.DONE)

    def get_done(self,sourcename,step):
        return redis_.get(self.done_name(sourcename,step))

    def clear(self):
        for key in redis_.keys(self.name+"_*"):
            redis_.delete(key)

    def query(self):
        download_url_step=1
        download_pdf_step=2
        for sn in self.get_sourcenames():
            print("sourname : "+sn)
            if self.get_done(sn,download_url_step) == self.DONE:
                if self.get_done(sn,download_pdf_step) == self.DONE:
                    print(sn+" 已经全部完成！")
                else:
                    print("下载链接已完成，正在下载PDF...")
                    print("PDF剩余数："+str(redis_.llen(self.fix(sn,download_pdf_step-1))))
            else:
                print("正在解析下载链接...")
                print("链接剩余数量："+str(redis_.llen(self.fix(sn,download_url_step-1))))

    def query_finsh_url(self):
        for sn in self.get_sourcenames():
            print("sourname : " + sn,"已完成数量："+str(redis_.llen(self.fix(sn,2))))



if __name__ == '__main__':
    for key in redis_.keys("*"):
        redis_.delete(key)
        print(key ,redis_.type(key))
        if redis_.type(key) == "string":
            print(key,redis_.get(key))
        elif redis_.type(key) == "set":
            print(key," : ",redis_.scard(key)," : ",redis_.smembers(key))
        elif redis_.type(key) =="list":
            print(key ," : ",redis_.llen(key)," : ", redis_.lrange(key,0,100))
    

    # collect.check_task("mc0108")


    # collect.check_conf()

