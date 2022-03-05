# collection-scripts
Some useful scripts  for VCB-S collection work

## CRC32 checksum

Require zlib. For Windows, you can find an install scrpit at [zlib.install
](https://github.com/horta/zlib.install)

Simply drug the files to the script. or run the following command.

```powershell
python .\CRC32.py file1 file2 ...
```

The result will be printed on the screen and saved to the `result.txt` file.

## Renamer

Require a text file named `name_list.txt`, which contains all the names you want to change to, one item for each line. Put it by the script.

Drug the files you want to change to the script.
