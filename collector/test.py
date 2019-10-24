#!/usr/bin/python
#-*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os
import PyPDF2
from collector import htmls

def create_arff(file_path,attrs,name):
    arff_file=open("C:/temp/"+name+".arff","w+")
    arff_file.write("@relation order\n")
    for attr in attrs:
        arff_file.write("@attribute "+attr+" {'0','1'}\n")
    arff_file.write("@data\n")

    for line in open(file_path).readlines():
        # print(line)
        write_line=""
        keys = line.replace("\n", "").split(",")
        for attr in attrs:
            find=False
            for key in keys:
                if key == "":
                    continue
                if attr==key:
                    write_line+="'1',"
                    find=True
            if not find:
                write_line += "'0',"
        arff_file.write(write_line[:-1]+"\n")
        # print(write_line[:-1])

def checkpdf(file):

    try:
        pdffile = open(file, "rb+")
        pdf = PyPDF2.PdfFileReader(pdffile, strict=False)
        num=pdf.getNumPages()
        pdffile.close()
        return num
    except:

        try:
            pdffile.close()
            os.remove(file)
        except:
           pass
        raise ValueError("PDF出错！")


def test(url,file_path=r"C:\temp\other\test.pdf"):
    r = requests.get(url)
    try:
        c1 = r.cookies['BIGipServerlbapp_tc3']
        c2 = r.cookies['BIGipServerwww.osti.gov_pool']
        c3 = r.cookies['JSESSIONID']
    except:
        pass
    soup = BeautifulSoup(r.text, "html.parser")

    mate=soup.find("meta", {"name": "citation_pdf_url"})
    if mate==None:
        start_break=False
        for div1 in soup.find_all("div",class_="biblio-secondary-group"):
            for div2 in div1.find_all("div",class_="biblio-secondary-item small"):
                for a in div2.find_all("a"):
                    if "href" in a.attrs.keys():
                        if "https://doi.org" in a["href"]:
                            turl=a["href"]
                            cp=htmls.config_parser()
                            ht=htmls.HTML(None,None,None,None)
                            for conf in cp.get_all_conf():
                                print(conf)
                                if ht.test(conf,turl):
                                    result = ht.do_run(conf, turl)
                                    r2 = requests.get(result)
                                    r2.encoding = 'utf-8'
                                    # print(r2.text)
                                    file = open(file_path, "wb+")
                                    file.write(r2.content)
                                    file.close()
                                    break

                            start_break=True
                            break
                if start_break:
                    break
            if start_break:
                break

    else:
        pdf_url = mate["content"]
        cookies = {
            'BIGipServerlbapp_tc3': c1,
            'BIGipServerwww.osti.gov_pool': c2,
            'JSESSIONID': c3,
            '__utma': '249692800.1749221367.1564467097.1564467097.1564467097.1',
            '__utmc': '249692800',
            '__utmz': '249692800.1564467097.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
            '_ga': 'GA1.2.1749221367.1564467097',
            '_gid': 'GA1.2.298248318.1564467099',
            '__utmt': '1',
            '__utmb': '249692800.63.10.1564467097'
        }


        r2 = requests.get(pdf_url, cookies=cookies)
        r2.encoding = 'utf-8'
        # print(r2.text)
        file = open(file_path, "wb+")
        file.write(r2.content)
        file.close()
    page =checkpdf(file_path)
    print(page)




if __name__ == '__main__':
    test("https://www.osti.gov/biblio/1457174")


    # path = "C:/temp/part-r-2017"
    # attrs = {}
    # for line in open(path).readlines():
    #     keys = line.replace("\n", "").split(",")
    #     for key in keys:
    #         if key == "":
    #             continue
    #         if key in attrs:
    #             attrs[key] += 1
    #         else:
    #             attrs[key] = 1
    # # print(attrs)
    # sort_attrs = sorted(attrs.items(), key=lambda d: d[1], reverse=True)
    # # print(sort_attrs)
    # attr_list = []
    # for attr in sort_attrs:
    #     print(type(attr), attr, attr[0])
    #     attr_list.append(attr[0])
    #
    # create_arff(path,attr_list,"test")

