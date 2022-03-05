from cgitb import text
import sys, os
import zlib


if sys.version_info[:2] < (3, 6):
    print("The fxxx programmer is too lazy to check any support for Python 3.6-")
    input("Press ENTER to exit...")
    sys.exit(1)

file_list = sys.argv[1:]
text  = open("result.txt", "w+")
text.close()

print("输入 {} 个文件".format(len(file_list)))
for f in file_list:
    file = open(f, 'rb')
    hash = 0
    while True:
        s = file.read(65536)
        if not s:
            break
        hash = zlib.crc32(s, hash)
    hash = "{:08X}".format(hash)
    print(hash)
    file.close()
    text = open("result.txt", "a+")
    text.write(hash)
    text.write("\n")
    text.close()

sys.exit(1)
