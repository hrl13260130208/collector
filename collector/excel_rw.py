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



class File_Reader():
    def __init__(self,um):
        self.um=um
        self.step = 0
        self.write_step = 2

    def read(self,file_path,sourcename="doaj",issn="d"):
        logger.info("设定sourcename为："+sourcename+",开始读取文件...")
        self.um.save_sourcenames(sourcename)
        with open(file_path,"r",encoding="utf-8") as f:
            for line_index,line in enumerate(f.readlines()):
                eb = name_manager.execl_bean()
                eb.sourcename=sourcename
                eb.eissn=issn+str(line_index)
                eb.pinjie=line.replace("\n","").strip()
                eb.row_num=-1

                self.um.save(eb, self.step)

    def write(self,file_path):
        write_file=open(file_path,"w+",encoding="utf-8")
        back_file = open(file_path.replace(".txt", "_back.txt"), "w+",encoding="utf-8")
        logger.info("写入文件...")
        for sn in self.um.get_sourcenames():
            while (True):
                url_name = self.um.fix(sn, self.write_step)
                string = self.um.get_eb(url_name)
                if string == None:
                    break
                back_file.write(string + "\n")
                eb = name_manager.execl_bean()
                eb.paser(string)
                write_file.write(eb.pinjie+"##"+eb.full_url+"##"+eb.full_path+"\n")




def create_excel():
    file=open(r"C:\Users\zhaozhijie.CNPIEC\Documents\Tencent Files\2046391563\FileRecv\doajurl.txt","r",encoding="utf-8")
    values=["SOURCENAME","ISSN","EISSN","WAIBUAID","PINJIE","FULL_URL","ABS_URL","FULL_PATH"]
    dir_=r"C:\public\目次采全文\0924\doaj"
    sourcename="doaj"
    issn="d"
    index=0
    excel_index=0
    wb=None
    sheet=None
    for line_index,line in enumerate(file.readlines()):
        # print(line)
        # url="https://nepis.epa.gov/Exe/ZyPDF.cgi/"+line[-13:-5]+".PDF?Dockey="+line[-13:-5]+".PDF"

        if index==0:
            wb=xlwt.Workbook(encoding="utf-8")
            sheet=wb.add_sheet("Sheet1")
            index+=1
            for i,v in enumerate(values):
                sheet.write(0,i,v)
        elif index>60000:
            wb.save(dir_+"_"+str(excel_index)+".xls")
            index=0
            excel_index+=1
        else:
            sheet.write(index,values.index("SOURCENAME"),sourcename)
            sheet.write(index,values.index("ISSN"),issn+str(line_index))
            sheet.write(index,values.index("PINJIE"),line.replace("\n","").strip())
            # sheet.write(index,values.index("FULL_URL"),line.strip())
            index+=1
    wb.save(dir_+"_"+str(excel_index)+".xls")

def back_file_to_excel(back_file_path,excel_path):
    excels(excel_path,None).back_file_to_excel(back_file_path)




if __name__ == '__main__':
    create_excel()
    # name="dfsf"
    # um = name_manager.url_manager(name)
    # file_path = "C:/Users/zhaozhijie.CNPIEC/Desktop/temp/中信所待补全文清单_20181219..xls"
    # ex=excels(file_path,um)
    # ex.read()
    # ex.write()
    # create_excel()
    # back_file_to_excel(r"C:\public\目次采全文\0801\osti_0_back.txt",r"C:\public\目次采全文\0801\osti_0.xls")



