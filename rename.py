import xlrd
import os
import shutil

def rename(excel_name,dir=r"D:\data\0730",new_dir=r"D:\data\0730\osti"):
    rb = xlrd.open_workbook(excel_name)
    r_sheet = rb.sheet_by_index(0)

    list = r_sheet.row_values(0)

    url_num = list.index("PINJIE")
    full_path_num = list.index("FULL_PATH")
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)

    for row in range(r_sheet.nrows - 1):

        url = r_sheet.cell(row + 1, url_num).value
        full_path = r_sheet.cell(row + 1, full_path_num).value

        if full_path!="":
            path=os.path.join(dir,full_path)
            if os.path.exists(path):
                new_name=url[url.rfind("/")+1:]
                print(new_dir)
                new_path=os.path.join(new_dir,new_name+".pdf")
                print(url, new_name,new_path,path)
                shutil.copyfile(path, new_path)
            # print(url, full_path)



def rename2(pdf_dir="",txt=""):
    f=open(txt,"w+",encoding="utf-8")

    pdfs = set()
    for name in os.listdir(pdf_dir):
        pdfs.add(name.replace(".pdf",""))


    for i in range(11):
        excel_name=r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_"+str(i)+".xls"

        rb = xlrd.open_workbook(excel_name)
        r_sheet = rb.sheet_by_index(0)

        list = r_sheet.row_values(0)

        url_num = list.index("PINJIE")
        full_path_num = list.index("FULL_PATH")


        for row in range(r_sheet.nrows - 1):

            url = r_sheet.cell(row + 1, url_num).value
            full_path = r_sheet.cell(row + 1, full_path_num).value

            if full_path != "":
                path = os.path.join(dir, full_path)
                if os.path.exists(path):
                    new_name = url[url.rfind("/") + 1:]
                    if not new_name in pdfs:
                        f.write(url+","+new_name+","+path+"\n")
        break



def rename3(txt="",dir=""):
    dir=r"Z:\Backup\FTP_PDF\Report\doe\hb\new_pdf\osti"
    f = open(txt, encoding="utf-8")
    for line in f.readlines():
        items=line.replace("\n","").split(",")
        new_path=os.path.join(dir,items[1]+".pdf")
        shutil.copyfile(items[2], new_path)
        

def rename4():
    txt = r"Z:\Backup\FTP_PDF\Report\doe\hb\pdfs.txt"
    dir = r"Z:\Backup\FTP_PDF\Report\doe\hb\new_pdf\osti"

    pdfs = set()
    for name in os.listdir(dir):
        pdfs.add(name.replace(".pdf", ""))

    f = open(txt, encoding="utf-8")
    for line in f.readlines():

        items = line.replace("\n", "").split(",")
        if os.path.exists(items[2]):
            if items[1] not in pdfs:
                new_path = os.path.join(dir, items[1] + ".pdf")
                shutil.copyfile(items[2], new_path)


def rename5():
    dir=r"Z:\Backup\FTP_PDF\Report"
    new_dir=r"Z:\Backup\FTP_PDF\Report\NASA_PDF"
    f1 = open(r"Z:\Backup\FTP_PDF\Report\doe\nasa1.txt", "w+", encoding="utf-8")
    f2 = open(r"Z:\Backup\FTP_PDF\Report\doe\nasa2.txt", "w+", encoding="utf-8")
    excels=[r"Z:\Backup\FTP_PDF\Report\NASA-NEW目次\0724_1.xls",
            r"Z:\Backup\FTP_PDF\Report\NASA-NEW目次\0724_2.xls",
            r"Z:\Backup\FTP_PDF\Report\NASA目次\1.xls",
            r"Z:\Backup\FTP_PDF\Report\NASA目次\2.xls",
            r"Z:\Backup\FTP_PDF\Report\NASA目次\3.xls",
            r"Z:\Backup\FTP_PDF\Report\NASA目次\4.xls",
            r"Z:\Backup\FTP_PDF\Report\NASA目次\5.xls"]



    d = {}
    for excel_name in excels:
        rb = xlrd.open_workbook(excel_name)
        r_sheet = rb.sheet_by_index(0)

        list = r_sheet.row_values(0)

        url_num = list.index("PINJIE")
        full_path_num = list.index("FULL_PATH")
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)

        for row in range(r_sheet.nrows - 1):

            url = r_sheet.cell(row + 1, url_num).value
            full_path = r_sheet.cell(row + 1, full_path_num).value

            if full_path != "":
                new_name = url[url.rfind("/") + 1:]
                if new_name in d.keys():
                    d[new_name].append(url)
                else:
                    d[new_name] = [url]
    for key in d.keys():
        if len(d[key])==1:
            f1.write(str(key)+","+str(d[key]))
        else:
            f2.write(str(key)+","+str(d[key]))


if __name__ == '__main__':
    rename5()
    # os.remove()
    # rename3(txt=r"Z:\Backup\FTP_PDF\Report\doe\hb\pdfs.txt")
    # rename2(pdf_dir="",txt="")
    # rename(r"D:\data\0730\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")
    # rename(r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")
    # rename(r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")
    # rename(r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")
    # rename(r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")
    # rename(r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")
    # rename(r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")
    # rename(r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")
    # rename(r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")
    # rename(r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")
    # rename(r"Z:\Backup\FTP_PDF\Report\doe\合并\osti_9.xls",dir=r"Z:\Backup\FTP_PDF\Report\doe\合并",new_dir=r"Z:\Backup\FTP_PDF\Report\doe\合并\重命名\osti")




