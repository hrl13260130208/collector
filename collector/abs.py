#!/usr/bin/python
#-*- coding: utf-8 -*-

from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import *
import re
import xlrd
import xlwt
from  xlutils import copy
import os
import logging
import PyPDF2
from pdf2image import convert_from_path
import string
import pytesseract

logging.basicConfig(level = logging.ERROR,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger("Ilogger")

def read(file):
    #打开一个pdf文件
    fp = open(file, 'rb')
    #创建一个PDF文档解析器对象
    parser = PDFParser(fp)
    #创建一个PDF文档对象存储文档结构
    #提供密码初始化，没有就不用传该参数
    #document = PDFDocument(parser, password)
    document = PDFDocument(parser)
    #检查文件是否允许文本提取
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    #创建一个PDF资源管理器对象来存储共享资源
    #caching = False不缓存
    rsrcmgr = PDFResourceManager(caching = False)
    # 创建一个PDF设备对象
    laparams = LAParams()
    # 创建一个PDF页面聚合对象
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    #创建一个PDF解析器对象
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    #处理文档当中的每个页面

    # doc.get_pages() 获取page列表
    #for i, page in enumerate(document.get_pages()):
    #PDFPage.create_pages(document) 获取page列表的另一种方式
    replace=re.compile(r'\n')
    # 循环遍历列表，每次处理一个page的内容
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        # 接受该页面的LTPage对象
        layout=device.get_result()
        # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象
        # 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等
        # print("======================")
        for x in layout:
            #如果x是水平文本对象的话
            # print("+++++++++++",type(x))
            # if(isinstance(x,LTTextBoxHorizontal)):
            #     text=re.sub(replace,'',x.get_text())
            #     print(text)
            #     if len(text)>500:
            #         return text[:text.rfind(".")]
            # print(x)
            line=x.get_text().strip()
            # print(line)
            if len(line)>600:
                a=line.find(".")
                b=line.find("。")
                if "  " in line:
                    continue
                if "(cid:" in line:
                    line=re.sub("\(cid:.+\)","",line)
                if a!=-1:
                    line=line[:line.rfind(".")+1]
                if b!=-1:
                    line=line[:line.rfind("。")+1]
                if len(line)>50:
                    return line
class excels():
    def __init__(self,file_path):
        self.file_path=file_path
        self.values=["path","abstract"]
        self.nums={}

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
            print(value)
            print(self.list)
            index = self.list.index(value)
            self.nums[value]=index
        # self.nums["path"]=

    def read(self):

        # self.create()
        print("====")
        for row in range(self.r_sheet.nrows-1):
            row_num=row+1
            print(row_num)
            path=self.r_sheet.cell(row_num,self.nums["path"]).value
            abs=self.r_sheet.cell(row_num,self.nums["abstract"]).value
            print(abs)
            if abs!="":
                continue
            if os.path.exists(path):
                try:
                    print("读取PDF："+path+"...")
                    # text=read(path)
                    # text=text.replace("\n"," ").replace("Abstract:","").replace("Abstract","").strip()
                    pdf_file=open(path, "rb")
                    pdf = PyPDF2.PdfFileReader(pdf_file, strict=False)
                    if pdf.getNumPages()>100:
                        pdf_file.close()
                        continue
                    pdf_file.close()
                    text=ocr_read(path)
                    text = text.replace("\n", " ")
                    print(text)
                    self.write(text,row_num)
                except:
                    logger.error("err",exc_info=True)
            else:
                print("路径不存在！")
        self.save()



    def write(self,text,row_num):
        self.w_sheet.write(row_num,self.nums["abstract"],text)


    def save(self):
        self.wb.save(self.file_path)

def py2pdf_read(path):
    file=open(path, "rb")
    pdf = PyPDF2.PdfFileReader(file, strict=False)
    print(pdf.getNumPages())
    print(pdf.getFormTextFields())

def ocr_read(filename):
    print('filename=', filename)
    outputDir="C:/temp/png"

    images = convert_from_path(filename)
    for index, img in enumerate(images):
        if index > 2:
            break
        image_path = '%s/page_%s.png' % (outputDir, index)
        print(image_path)
        img.save(image_path)
        text=get_abs(pytesseract.image_to_string(image_path))
        if text!=None:
            return text
def get_abs(text):
    abs_num=text.lower().find("abstract")
    if abs_num!=-1:
        keywords_num=text.lower().find("keywords")
        if keywords_num!=-1:
            if keywords_num<abs_num+8:
                for section in get_sections(text):
                    if section.__len__() > 500:
                        num = section.rfind(".")
                        if num > 500:
                            return abs_clear(section[:num + 1])
            else:
                return abs_clear(text[abs_num+8:keywords_num])
        else:
            # print(text)
            abs=""
            for section in get_sections(text[abs_num+8:]):
                if section.__len__()>500:
                    abs=section
                    break
                else:
                    abs+=section+"\n"
                    if abs.__len__()>500:
                        break
            return abs_clear(abs)
    else:
        for section in get_sections(text):
            if section.__len__()>500:
                num=section.rfind(".")
                if num >500:
                    return abs_clear(section[:num+1])


def get_sections(text):
    return text.split("\n\n")

def is_abs(abs):
    d = u = l = o = 0
    print("---------------------------")

    if "@" in abs:
        print("有@符号！")
        return False
    for i in range(len(abs)):
        if abs[i] in string.digits:
            d += 1
        elif abs[i] in string.ascii_uppercase:
            u += 1
        elif abs[i] in string.ascii_lowercase:
            l += 1
        elif abs[i] in string.punctuation:
            o += 1

    print("数字：",d,d/abs.__len__())
    if d/abs.__len__()>0.01:
        return False
    print("大写字母：",u,u/abs.__len__())
    if u/ abs.__len__() > 0.05:
        return False
    print("小写字母：",l,l/abs.__len__())
    print("标点特殊字符：",o,o/abs.__len__())
    if u/ abs.__len__() > 0.1:
        return False

    return True




def abs_clear(abs):
    if is_abs(abs):
        abs=abs_head_clear(abs.strip())
        print("last char:",abs[-1])
        if abs[-1] !="." and abs[-1] !="。":
            abs=abs+"."
        return abs
def abs_head_clear(abs):
    if abs[0].isalpha():
        if abs[0].islower():
            abs=abs[0].upper()+abs[1:]
        return abs
    else:
        return abs_head_clear(abs[1:])
def run(excel_path):
    '''
    Excel 要求：Excel第一行为列名，必须有列（）：path，abstract
                path：pdf路径
                abstract：需要补的摘要

    :param excel_path:
    :return:
    '''
    excels(excel_path).read()

def run_dir(dir):
    wb = xlwt.Workbook(encoding="utf-8")
    sheet1=wb.add_sheet("sheet1")
    sheet1.write(0, 0, "path")
    sheet1.write(0, 1, "abstract")
    for index,file in enumerate(os.listdir(dir)):
        print(file)
        path=os.path.join(dir,file)
        print(path)


        pdf_file = open(path, "rb")
        pdf = PyPDF2.PdfFileReader(pdf_file, strict=False)
        if pdf.getNumPages() > 100:
            pdf_file.close()
            continue
        pdf_file.close()
        text = ocr_read_jpn(path)
        # text = text.replace("\n", " ")
        # print(text)
        # sheet1.write(index+1,0,path)
        # sheet1.write(index+1,1,text)

    wb.save("C:/temp/a.xls")

def ocr_read_jpn(filename):
    print('filename=', filename)
    outputDir = "C:/temp/png"

    images = convert_from_path(filename)
    for index, img in enumerate(images):
        if index > 2:
            break
        image_path = '%s/page_%s.png' % (outputDir, index)
        print(image_path)
        img.save(image_path)
        print(pytesseract.image_to_string(image_path))
        # text = get_abs(pytesseract.image_to_string(image_path,lang="jpn"))
        # if text != None:
        #     return text

if __name__ == '__main__':
    # run("C:/execl/aae6.xlsx")
    # run("C:/public/目次采全文/0617/中信所缺失摘要清单_20190621..xls")
    print(ocr_read("G:/hrl/0621/中信/zx0621-c3/4efec686940f11e9abe8b083fe6ed898.pdf"))
    # run_dir("C:/temp/新建文件夹")
    # path="C:/pdfs/iccm"
    # c_path="C:/temp/train"
    # for file in os.listdir(path):
    #     file_path=os.path.join(path,file)
    #     print(file_path)
    #     img=convert_from_path(file_path)
    #     img[0].save(os.path.join(c_path,file.replace(".pdf",".jpg")))


    # excels("C:/temp/ISTS1.xls").read()
    # path="C:/temp/oRxeC5q6BgOl.pdf"
    # read(path)
    # path="Z:/数据组内部共享/中信所2019年任务/132/1-東光高岳-69874\httpswww.tktk.co.jpresearchreportpdf2014giho2014_27.pdf"
    # print("=============",read(path))

    # path="Z:/数据组内部共享/中信所2019年任务/补摘要/Japan Society for Aeronautical and Space Sciences 抽/ISTS1/6RyKnw4m14tQ.pdf"
    # py2pdf_read(path)



