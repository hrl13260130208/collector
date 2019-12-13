
from collector import excel_rw
from py2neo import Graph
from py2neo import Node
from py2neo import Relationship
import os

neo4j_host="10.3.1.99"
graph=Graph(host=neo4j_host,auth=("neo4j","1q2w3e"))

#label
SOURCE="source"
DONE="done"
NOPDF="nopdf"
NOTDONE="notdone"
ARTICLE="article"
RSA="RSA"

#item name
SOURCENAME="sourcename"
ISSN="issn"
WAIBUAID="waibuaid"
PINJIE="pinjie"
FULL_URL="full_url"
ABS_URL="abs_url"
FULL_PATH="full_path"
PAGE="page"
URL="url"

STRING_NOPDF="No pdf"
class neo_manager:
    def create_node_by_dict(self,labels,property):
        '''
        创建节点与属性
        :param label_name:
        :param property:
        :return:
        '''
        string = "create (n"
        for label in labels:
            string+=":"+label
        string+="{"

        for i in property.keys():
            string += i + ":\"" + str(property[i]) + "\","

        string = string[:-1]
        string += "}) return n"
        return graph.run(string).data()

    def create_unique(self):
        graph.run("CREATE CONSTRAINT ON (n:article) ASSERT n.url IS UNIQUE")

    def create_relationship(self, node1, node2, relationship_label_name):
        '''
        创建两个节点间的关系，节点为Node对象
        :param node1:
        :param node2:
        :param relationship_label_name:
        :return:
        '''
        return graph.create(Relationship(node1, relationship_label_name, node2))

    def match_by_dict(self, labels, property={}):
        '''
        通过传入的标签名与属性生成查询语句进行查询
        :param label_name:
        :param property:
        :return:
        '''

        string = "match (n"
        for label in labels:
            string+=":"+label
        string+="{"

        for i in property.keys():
            string += i + ":\"" + property[i] + "\","
        if len(property.keys())!=0:
            string = string[:-1]
        string += "}) return n"
        print(string)
        return graph.run(string).data()
    def parser_to_node(self,list):
        nodes=[]
        for l in list:
            nodes.append(l["n"])
        return nodes

    def update_to_database(self,node):
        '''
        更新节点到数据库
        :param node:
        :return:
        '''
        graph.push(node)
    def match_source(self,source):
        string='MATCH (n:source{sourcename:"'+source+'"})-[r]->(na) RETURN na'
        print(string)
        return graph.run(string).data()
'''
将数据存储到neo4j中，方便对数据的修改更新分类
'''
class MergeExcels():
    def __init__(self,create_unique=False):
        self.nm=neo_manager()
        if create_unique:
            self.nm.create_unique()

    def read_dir(self,dir):
        for file_name in os.listdir(dir):
            if ".xls" in file_name and ".xlsx" not in file_name:
                print(file_name)
                path=os.path.join(dir,file_name)
                print("读取文件：",path)
                self.read_excel(path)

    def read_excel(self,excel_path):
        excel=excel_rw.excels(excel_path,None)
        for eb in excel.read_items():
            self.create_node(eb)
    def update(self,excel_path,add_sources=False):
        excel = excel_rw.excels(excel_path, None)
        for eb in excel.read_items():
            n=self.nm.match_by_dict([ARTICLE],{URL:self.get_url(eb)})
            node =self.nm.parser_to_node(n)[0]
            if add_sources:
                self.add_source(node,eb)
            if node.has_label(DONE):
                continue
            else:
                if eb.is_done():
                    node.add_label(DONE)
                    node.remove_label(NOTDONE)

                    if eb.done == True:
                        node.add_label(NOPDF)
                        node[FULL_PATH]=eb.full_path
                    else:
                        node.setdefault(FULL_URL,eb.full_url)
                        node[FULL_URL]=eb.full_url
                        node[ABS_URL]=eb.abs_url
                        node[FULL_PATH]=eb.full_path
                        node[PAGE]=eb.page
            self.nm.update_to_database(node)


    def add_source(self,node,eb):
        sn = self.nm.match_by_dict([SOURCE], {SOURCENAME: eb.sourcename})
        if len(sn) == 0:
            sn = self.nm.create_node_by_dict([SOURCE], {SOURCENAME: eb.sourcename})
        snode = self.nm.parser_to_node(sn)[0]
        self.nm.create_relationship(snode, node, RSA)

    def get_url(self,eb):
        '''
        从传入的eb对象中找出可以作为其唯一标识的url
        :param eb:
        :return:
        '''
        return eb.pinjie



    def create_node(self,eb):
        url=self.get_url(eb)
        eb_property={URL:url,
                     ISSN:eb.eissn,
                     WAIBUAID:eb.waibuaid,
                     PINJIE:eb.pinjie,
                     FULL_URL:eb.full_url,
                     ABS_URL:eb.abs_url,
                     FULL_PATH:eb.full_path,
                     PAGE:eb.page}
        labels=set()
        if eb.is_done():
            labels.add(DONE)
            if eb.done==True:
                labels.add(NOPDF)
        else:
            labels.add(NOTDONE)
        labels.add(ARTICLE)
        n=self.nm.create_node_by_dict(labels,eb_property)
        node=self.nm.parser_to_node(n)[0]
        self.add_source(node,eb)

    def export(self,txt_path,labels=[ARTICLE],items=[FULL_URL,ABS_URL,FULL_PATH,PAGE]):
        with open(txt_path,"w+",encoding="utf-8") as f:
            f_line=""
            for i in items:
                f_line+=i+"##"

            f.write(f_line[:-2]+"\n")
            n=self.nm.match_by_dict(labels)
            for node in self.nm.parser_to_node(n):
                line = ""
                for i in items:
                    value=node.get(i)
                    if value==None or value=="":
                        value="$$"
                    line += value + "##"
                f.write(line[:-2]+"\n")

    def query(self,labels=[ARTICLE]):
        n = self.nm.match_by_dict(labels)
        print(len(n))

    def query_source(self,sourcename):
        n=self.nm.match_source(sourcename)
        print(len(n))


if __name__ == '__main__':
    # MergeExcels().read_excel(r"C:\temp\test.xls")
    # MergeExcels().read_dir(r"C:\temp\osti")
    # MergeExcels().update(r"C:\temp\osti\r1119\web_xls\springer.xls",add_sources=True)
    # MergeExcels().export(r"C:\temp\test.txt")
    # MergeExcels().query(labels=[NOTDONE])
    MergeExcels().query_source("springer")





