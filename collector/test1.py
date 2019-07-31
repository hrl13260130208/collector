import os

def write_excel():
    path="/home/pdfs/1.xls"
    dirs=path.split("/")
    print(dirs[-2]+"/"+dirs[-1])

if __name__ == '__main__':
    # 写入Excel
    write_excel()
    print ('写入成功')
