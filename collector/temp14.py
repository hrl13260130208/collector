import collector.collect as collect
import collector.htmls as htmls



# redis_ = redis.Redis(host="10.3.1.99", port=6379, db=1,decode_responses=True)
# print(redis_.keys("*"))

if __name__ == '__main__':
    name = "osti_1"
    # name = "hg0903"


    file_path = r"C:\public\目次采全文\0730\osti_1.xls"
    # file_path = r"C:\public\目次采全文\0903\化工所待补全文清单_20190903..xls"



    cp = htmls.config_parser()
    cp.paser()
    collect.run_thread(name, file_path)
    cp.backup()


    # collect.test_download()