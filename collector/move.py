import os
import shutil

def move():
    copy_path = "C:/temp/a/"

    write_file = open(r"C:\pdfs\list.txt")
    if not os.path.exists(copy_path):
        os.mkdir(copy_path)
    for line in write_file.readlines():
        if line.replace("\n", "") == "":
            continue
        file_name = line.replace("\n", "")
        path = "C:/pdfs/" + file_name
        print(path)
        if os.path.exists(path):
            print("复制文件：" + file_name)
            shutil.copyfile(path, copy_path + file_name)

if __name__ == '__main__':
    move()

