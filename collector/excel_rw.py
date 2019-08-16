import xlrd
from  xlutils import copy
from collector import  name_manager
import logging
from collector import collect
import os
import xlwt





logger = logging.getLogger("logger")
class excels():
    def __init__(self,file_path,um):
        self.file_path=file_path
        self.um=um
        self.values=["SOURCENAME","ISSN","EISSN","WAIBUAID","PINJIE","FULL_URL","ABS_URL","FULL_PATH"]
        self.step=0
        # self.save_path="C:/pdfs/excel.xls"
        self.report_path=collect.REPORT_PATH
        self.write_step=2
        self.report_step=3
        self.nums=[]
        self.create()

    def create(self):
        rb = xlrd.open_workbook(self.file_path)
        self.r_sheet = rb.sheet_by_index(0)
        self.wb = copy.copy(rb)
        self.w_sheet = self.wb.get_sheet(0)
        self.init_nums()

    def init_nums(self):
        self.list = self.r_sheet.row_values(0)
        for value in self.values:
            index = self.list.index(value)
            self.nums.append(index)

    def read(self):
        logger.info("读取execl...")

        self.create()

        for row in range(self.r_sheet.nrows-1):
            eb=name_manager.execl_bean()
            eb.row_num=row+1
            eb.sourcename=self.r_sheet.cell(eb.row_num,self.nums[0]).value
            issn=self.r_sheet.cell(eb.row_num,self.nums[1]).value
            eissn=self.r_sheet.cell(eb.row_num,self.nums[2]).value
            if issn =="":
                eb.eissn=eissn
            elif(eissn == ""):
                eb.eissn=issn
            else:
                eb.eissn=issn+"-"+eissn
            eb.waibuaid=self.r_sheet.cell(eb.row_num,self.nums[3]).value
            eb.pinjie=self.r_sheet.cell(eb.row_num,self.nums[4]).value
            eb.full_url=self.r_sheet.cell(eb.row_num,self.nums[5]).value
            eb.abs_url=self.r_sheet.cell(eb.row_num,self.nums[6]).value
            eb.full_path=self.r_sheet.cell(eb.row_num,self.nums[7]).value
            if self.list.__len__()> self.nums[7]+1:
                page_num=self.r_sheet.cell(eb.row_num,self.nums[7]+1).value
                if page_num:
                    eb.page=int(page_num)

            eb.check()

            if not eb.is_done():
                logger.info(eb.to_string())
                self.um.save_sourcenames(eb.sourcename)
                self.um.save(eb,self.step)
        logger.info("execl读取完成。")

    def write(self):
        back_file=open(self.file_path.replace(".xls","_back.txt"),"w+")
        logger.info("写入execl...")
        for sn in self.um.get_sourcenames():
            while (True):
                url_name=self.um.fix(sn,self.write_step)
                string = self.um.get_eb(url_name)
                if string == None:
                    break
                back_file.write(string+"\n")
                eb =name_manager.execl_bean()
                eb.paser(string)
                self.excel_write(eb)
        self.wb.save(self.file_path)
        logger.info("Excel写入完成。")

    def report(self):
        file=open(self.report_path,"a+")
        for sn in self.um.get_sourcenames():
            while (True):
                url_name=self.um.fix(sn,self.report_step)
                string = self.um.get_eb(url_name)
                if string == None:
                    break
                file.write(string+"\n")

        logger.info("report文件写入完成。")

    def back_file_to_excel(self,back_file_path):
        back_file = open(back_file_path, "r")
        for line in back_file.readlines():
            eb = name_manager.execl_bean()
            eb.paser(line)
            self.excel_write(eb)
        self.wb.save(self.file_path)

    def excel_write(self,eb):
        print(os.path.exists(collect.first_dir + eb.full_path))
        if os.path.exists(collect.first_dir + eb.full_path):
            if len(eb.full_url)>150:
                eb.full_url=eb.abs_url
            self.w_sheet.write(eb.row_num, self.nums[5], eb.full_url)
            self.w_sheet.write(eb.row_num, self.nums[6], eb.abs_url)

            self.w_sheet.write(eb.row_num, self.nums[7], eb.full_path)
            self.w_sheet.write(eb.row_num, self.nums[7] + 1, eb.page)


def write_pages_and_absurl(excel_name):
    rb = xlrd.open_workbook(excel_name)
    r_sheet = rb.sheet_by_index(0)
    wb = copy.copy(rb)
    w_sheet = wb.get_sheet(0)
    list = r_sheet.row_values(0)

    total_pages_num = list.index("TOTALPAGES")
    pages_num = list.index("page")
    absurlnum=list.index("ABS_URL")
    url_num=list.index("PINJIE")
    pmc_num=list.index("WAIBUAID")
    sn_num=list.index("SOURCENAME")

    for row in range(r_sheet.nrows - 1):
        tp=r_sheet.cell(row+1,total_pages_num)
        abs_url=r_sheet.cell(row+1,absurlnum).value
        print("==============",tp.value)
        if tp.value=="":
            page=r_sheet.cell(row+1,pages_num)
            print(page)
            if page.value!="":
                w_sheet.write(row+1,total_pages_num,page.value)
        sn = r_sheet.cell(row + 1, sn_num)
        print(sn)
        if abs_url=="":
            sn=r_sheet.cell(row+1,sn_num)
            print(sn.value)
            if sn.value=="PMC":
                w_sheet.write(row + 1, absurlnum,"https://www.ncbi.nlm.nih.gov/pmc/articles/"+r_sheet.cell(row+1,pmc_num).value)
            else:
                w_sheet.write(row + 1, absurlnum, r_sheet.cell(row + 1,url_num).value)

    wb.save(excel_name)


def create_excel():
    file=open(r"C:\Users\zhaozhijie.CNPIEC\Documents\Tencent Files\2046391563\FileRecv\MobileFile\epa.txt","r")
    values=["SOURCENAME","ISSN","EISSN","WAIBUAID","PINJIE","FULL_URL","ABS_URL","FULL_PATH"]
    dir_=r"C:\public\目次采全文\0806\epa"
    sourcename="epa"
    issn="o1111"
    index=0
    excel_index=0
    wb=None
    sheet=None
    for line in file.readlines():
        print(line)
        url="https://nepis.epa.gov/Exe/ZyPDF.cgi/"+line[-13:-5]+".PDF?Dockey="+line[-13:-5]+".PDF"

        if index==0:
            wb=xlwt.Workbook(encoding="utf-8")
            sheet=wb.add_sheet("Sheet1")
            index+=1
            for i,v in enumerate(values):
                sheet.write(0,i,v)
        elif index>22000:
            wb.save(dir_+"_"+str(excel_index)+".xls")
            index=0
            excel_index+=1
        else:
            sheet.write(index,values.index("SOURCENAME"),sourcename)
            sheet.write(index,values.index("ISSN"),issn)
            sheet.write(index,values.index("PINJIE"),line.replace("\n","").strip())
            sheet.write(index,values.index("FULL_URL"),url)
            index+=1
    wb.save(dir_+"_"+str(excel_index)+".xls")

def back_file_to_excel(back_file_path,excel_path):
    excels(excel_path,None).back_file_to_excel(back_file_path)




if __name__ == '__main__':
    # name="dfsf"
    # um = name_manager.url_manager(name)
    # file_path = "C:/Users/zhaozhijie.CNPIEC/Desktop/temp/中信所待补全文清单_20181219..xls"
    # ex=excels(file_path,um)
    # ex.read()
    # ex.write()
    # write_pages_and_absurl("C:/public/目次采全文/0723/中信所待补全文清单_20190723..xls")
    create_excel()
    # back_file_to_excel(r"C:\public\目次采全文\0801\osti_0_back.txt",r"C:\public\目次采全文\0801\osti_0.xls")



