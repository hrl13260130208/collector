import collector.collect as collect
import collector.htmls as htmls



# redis_ = redis.Redis(host="10.3.1.99", port=6379, db=1,decode_responses=True)
# print(redis_.keys("*"))

if __name__ == '__main__':

    # name = "hg0621-c1"
    name = "jx0621"

    # file_path = "F:/hrl/mc/0121/冶金所待补全文清单_20190121..xls"
    # file_path = "F:/hrl/mc/0121/机械所待补全文清单_20190121..xls"
    # file_path = "F:/hrl/mc/0311/中信所待补全文清单_20190311..xls"
    # file_path = "F:/hrl/mc/other/pmc2018-2019待采全文的文章清单.xls"
    # file_path = "F:/hrl/mc/other/gruyter2018-2019待采全文的文章清单.xls"
    file_path = "C:/public/目次采全文/0617/机械所待补全文清单_20190621..xls"

    # check_task(name)
    cp = htmls.config_parser()
    cp.paser()
    collect.run_thread(name, file_path)
    cp.backup()


    # collect.test_download()