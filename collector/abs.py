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
from  xlutils import copy
import os

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
        print("======================")
        for x in layout:
            #如果x是水平文本对象的话
            print("+++++++++++",type(x))
            # if(isinstance(x,LTTextBoxHorizontal)):
            #     text=re.sub(replace,'',x.get_text())
            #     print(text)
            #     if len(text)>500:
            #         return text[:text.rfind(".")]
            line=x.get_text()
            print(line)
            if len(line)>100:
                a=line.find(".")
                b=line.find("。")
                if a!=-1:
                    return line[:line.rfind(".")+1]
                if b!=-1:
                    return line[:line.rfind("。")+1]
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
            index = self.list.index(value)
            self.nums[value]=index

    def read(self):

        # self.create()

        for row in range(self.r_sheet.nrows-1):
            row_num=row+1
            path=self.r_sheet.cell(row_num,self.nums["path"]).value
            if os.path.exists(path):
                try:
                    print("读取PDF："+path+"...")
                    text=read(path)
                    self.write(text,row_num)
                except:
                    pass
        self.save()



    def write(self,text,row_num):
        self.w_sheet.write(row_num,self.nums["abstract"],text)


    def save(self):
        self.wb.save(self.file_path)






if __name__ == '__main__':
    excels("C:/tmp/ASS.xls").read()
    # path="Z:/数据组内部共享/中信所2019年任务/132/1-東光高岳-69874\httpswww.tktk.co.jpresearchreportpdf2014giho2014_27.pdf"
    # print("=============",read(path))



