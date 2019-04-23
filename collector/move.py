import os
import shutil


if __name__ == '__main__':
    copy_path="C:/pdfs/members"
    name="2"
    write_file = open("C:/pdfs/list" + name + ".txt")
    if not os.path.exists(copy_path):
        os.mkdir(copy_path)
    for line in write_file.readlines():
        path = "C:/pdfs/"+line.replace("\n", "")
        print(path)
        file_name=path[path.rfind("/"):]
        print("复制文件："+file_name)
        shutil.copyfile(path,copy_path+file_name)





