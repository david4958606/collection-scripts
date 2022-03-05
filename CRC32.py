import sys, os
import zlib


if sys.version_info[:2] < (3, 6):
    print("The fxxx programmer is too lazy to check any support for Python 3.6-")
    input("Press ENTER to exit...")
    sys.exit(1)

file_list = sys.argv[1:]
result  = open("result.txt", "w+")
result.close()

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
    result = open("result.txt", "a+")
    result.write(hash)
    result.write("\n")
    result.close()

sys.exit(1)
