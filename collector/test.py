#!/usr/bin/python
#-*- coding: utf-8 -*-


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



if __name__ == '__main__':

    path = "C:/temp/part-r-2017"
    attrs = {}
    for line in open(path).readlines():
        keys = line.replace("\n", "").split(",")
        for key in keys:
            if key == "":
                continue
            if key in attrs:
                attrs[key] += 1
            else:
                attrs[key] = 1
    # print(attrs)
    sort_attrs = sorted(attrs.items(), key=lambda d: d[1], reverse=True)
    # print(sort_attrs)
    attr_list = []
    for attr in sort_attrs:
        print(type(attr), attr, attr[0])
        attr_list.append(attr[0])

    create_arff(path,attr_list,"test")

