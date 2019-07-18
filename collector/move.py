import os
import shutil


if __name__ == '__main__':
    copy_path="C:/pdfs/iccm13"
    name="15"
    write_file = open("C:/pdfs/list" + name + ".txt")
    if not os.path.exists(copy_path):
        os.mkdir(copy_path)
    for line in write_file.readlines():
        if line.replace("\n", "")=="":
            continue
        path = "C:/pdfs/"+line.replace("\n", "")
        print(path)
        if os.path.exists(path):
            file_name=line.replace("\n", "")
            print("复制文件："+file_name)
            shutil.copyfile(path,copy_path+file_name)

