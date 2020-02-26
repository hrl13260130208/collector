
import requests
from bs4 import BeautifulSoup
import time
import os

def test():
    list=["http://accelconf.web.cern.ch/AccelConf/ERL2015/","http://accelconf.web.cern.ch/AccelConf/erl2017/","http://accelconf.web.cern.ch/AccelConf/HIAT2015/","http://accelconf.web.cern.ch/AccelConf/fls2018/","http://accelconf.web.cern.ch/AccelConf/HB2010/","http://accelconf.web.cern.ch/AccelConf/HB2012/","http://accelconf.web.cern.ch/AccelConf/HB2014/","http://accelconf.web.cern.ch/AccelConf/hb2016/","http://accelconf.web.cern.ch/AccelConf/hb2018/","http://accelconf.web.cern.ch/AccelConf/IBIC2013/","http://accelconf.web.cern.ch/AccelConf/IBIC2014/","http://accelconf.web.cern.ch/AccelConf/IBIC2015/","http://accelconf.web.cern.ch/AccelConf/ibic2016/","http://accelconf.web.cern.ch/AccelConf/ibic2017/","http://accelconf.web.cern.ch/AccelConf/ICAP2012/","http://accelconf.web.cern.ch/AccelConf/ICAP2015/","http://accelconf.web.cern.ch/AccelConf/icap2018/","http://accelconf.web.cern.ch/AccelConf/icalepcs2011","http://accelconf.web.cern.ch/AccelConf/ICALEPCS2013/","http://accelconf.web.cern.ch/AccelConf/ICALEPCS2015/","http://accelconf.web.cern.ch/AccelConf/icalepcs2017/","http://accelconf.web.cern.ch/AccelConf/FEL2013/","http://accelconf.web.cern.ch/AccelConf/FEL2014/","http://accelconf.web.cern.ch/AccelConf/FEL2015/","http://accelconf.web.cern.ch/AccelConf/fel2017/","http://accelconf.web.cern.ch/AccelConf/Cyclotrons2010/","http://accelconf.web.cern.ch/AccelConf/CYCLOTRONS2013/","http://accelconf.web.cern.ch/AccelConf/cyclotrons2016/","http://accelconf.web.cern.ch/AccelConf/IPAC2013/","http://accelconf.web.cern.ch/AccelConf/IPAC2014/","http://accelconf.web.cern.ch/AccelConf/IPAC2015/","http://accelconf.web.cern.ch/AccelConf/ipac2016/","http://accelconf.web.cern.ch/AccelConf/ipac2017/","http://accelconf.web.cern.ch/AccelConf/ipac2018/","http://accelconf.web.cern.ch/AccelConf/ipac2019/","http://accelconf.web.cern.ch/AccelConf/ECRIS2012/","http://accelconf.web.cern.ch/AccelConf/ECRIS2014/","http://accelconf.web.cern.ch/AccelConf/ecris2016/","http://accelconf.web.cern.ch/AccelConf/ecris2018/","http://accelconf.web.cern.ch/AccelConf/PCaPAC2014/","http://accelconf.web.cern.ch/AccelConf/pcapac2016/","http://accelconf.web.cern.ch/AccelConf/pcapac2018/","http://accelconf.web.cern.ch/AccelConf/LINAC2014/","http://accelconf.web.cern.ch/AccelConf/linac2016/","http://accelconf.web.cern.ch/AccelConf/linac2018/","http://accelconf.web.cern.ch/AccelConf/COOL2013/","http://accelconf.web.cern.ch/AccelConf/cool2015/","http://accelconf.web.cern.ch/AccelConf/cool2017/","https://ref.ipac19.org/conference/show/641","http://accelconf.web.cern.ch/AccelConf/SRF2011/","http://accelconf.web.cern.ch/AccelConf/SRF2013/","http://accelconf.web.cern.ch/AccelConf/SRF2015/","http://accelconf.web.cern.ch/AccelConf/srf2017/"]
    f=open(r"C:\temp\新建文本文档3.txt","w+",encoding="utf-8")
    for url in list:
        print(url)
        try:
            data1=requests.get(url)
            s1=BeautifulSoup(data1.text,"html.parser")
            num=0
            url2=url+"html/class.htm"
            print("------",url2)
            data2=requests.get(url2.replace("class.htm","class1.htm"))
            s2=BeautifulSoup(data2.text,"html.parser")
            a_set=()
            author = "没作者"
            doi = "没doi"
            for a in s2.find_all("a"):
                url3=url2[:url2.rfind("/")+1]+a["href"]
                data3=requests.get(url3)
                s3=BeautifulSoup(data3.text,"html.parser")
                titles=s3.find_all("td",class_="paptitle")
                num+=len(titles)
                au=s3.find("span", class_="author_cl")
                if au!=None:
                    author="有作者"

                if "DOI" in s3.get_text():
                    doi="有doi"

            f.write(url + "##" + url2 + "##" + str(num)+"##"+doi+"##"+author + "\n")
        except:
            print("err")
            time.sleep(10)
def test2():
    dir=r"C:\temp\osti\r1119\web"
    all_file1=r"C:\temp\osti\r1119\web\all_wiley.txt"
    af1 = open(all_file1, "w+", encoding="utf-8")
    all_file=r"C:\temp\osti\r1119\web\all.txt"
    af=open(all_file,"w+",encoding="utf-8")
    for file in os.listdir(dir):
        if "wiley" in file:
            path=os.path.join(dir,file)
            f =open(path,encoding="utf-8")
            af1.write(f.read())
        else:
            path = os.path.join(dir, file)
            f = open(path, encoding="utf-8")
            af.write(f.read())



if __name__ == '__main__':
    # test2()
    url="https://www.atmos-chem-phys-discuss.net/15/19835/2015/"
    data=requests.get(url)
    print(data.text)





