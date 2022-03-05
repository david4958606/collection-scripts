import os, sys


file_list = sys.argv[1:]
list  = open("name_list.txt", "r+")
names = list.readlines()
list.close()

if len(file_list) != len(names):
    raise ValueError("定义文件名条目数与实际文件数不符！")

i = 0
for line in names:
    line = line.strip() # 去除文件名前后空格
    print(line)
    file = file_list[i]
    (path, name) = os.path.split(file) # 获取路径和文件名
    os.chdir(path)
    (pname, ext) = os.path.splitext(name) # 获取文件名和拓展名
    dst = line + ext # 给目标文件名加上拓展名
    os.rename(file, dst)
    print(dst)
    i = i + 1
