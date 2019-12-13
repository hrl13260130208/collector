import collector.collect as collect
import collector.htmls as htmls



# redis_ = redis.Redis(host="10.3.1.99", port=6379, db=1,decode_responses=True)
# print(redis_.keys("*"))

if __name__ == '__main__':
    name = "zx1108"
    file_path = r"C:\public\目次采全文\1108\中信所待补全文清单_20191106..xls"

    # name = "osti_12"
    #
    #
    # file_path = r"C:\public\目次采全文\0730\osti_12.xls"
    # check_task(name)
    cp = htmls.config_parser()
    cp.paser()
    collect.run_thread(name, file_path)
    cp.backup()


    # collect.test_download()