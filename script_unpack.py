import zlib
import os

data = open('script.arc', 'rb').read()

"""
script.arc 本质上是若干个 TXT 文本文档进行 zlib 压缩后整合起来的，整个文件的结构为：
1. 头 0x20 字节：文件头
2. 之后的主体：zlib 压缩后的 TXT 文件，每个压缩后 TXT 文件与 3. 中的条目一一对应
3. 之后的一小段：若干个条目，表示这些 TXT 文件压缩前后的一些信息，一个条目为 24 字节，固定结构
4. 最后的明文部分：TXT 文件名，每个文件名与 3. 中的条目一一对应

文件头结构：
0x00~0x04: 0x41524320 ("ARC ")
0x04~0x08: TXT 文件个数，即 3. 中的条目个数，乘以 24 （每个条目的字节长度）后即所有条目的总长度
0x08~0x0C: 未知，但似乎填零没影响
0x0C~0x10: 3. 开始的偏移地址
0x10~0x14: 4. 开始的偏移地址
0x14~0x18: 4. 的总长度
0x18~0x20：填零

3. 中 24 字节条目的结构：
0x00~0x04：条目对应的 TXT 文件名在 4. 中的偏移
0x04~0x08：条目对应的压缩后的 TXT 文件数据块在 script.arc 中的偏移地址
0x08~0x0C：压缩后 TXT 文本的大小
0x0C~0x10：未知，但其值似乎固定为 0x20
0x10~0x14：压缩前 TXT 文本的大小
0x14~0x18：未知，但实测填零没有影响
"""

assert data[:4] == b'ARC '
num_TXT = int.from_bytes(data[4:8], byteorder='little')
offset_entry = int.from_bytes(data[12:16], byteorder='little')
offset_txt_name = int.from_bytes(data[16:20], byteorder='little')

entry_data = data[offset_entry : offset_entry + 24 * num_TXT]
txt_name_data = data[offset_txt_name:]

if not os.path.exists('./TXTs'):
    os.mkdir('./TXTs')
for i in range(num_TXT):
    one_entry = entry_data[i * 24 : (i+1) * 24]

    # TXT 文件名
    txt_name = txt_name_data[int.from_bytes(one_entry[:4], byteorder='little'):].split(b'\x00')[0].decode('utf-8')
    # 压缩后 TXT 数据
    compressed_data = data[int.from_bytes(one_entry[4:8], byteorder='little') : int.from_bytes(one_entry[4:8], byteorder='little') + int.from_bytes(one_entry[8:12], byteorder='little')]
    # 解压后的 TXT 数据（应该的长度）
    supposed_decompressed_length = int.from_bytes(one_entry[16:20], byteorder='little')
    # Python 解压后的 TXT 数据
    decompressed_data = zlib.decompress(compressed_data)
    # 确认压缩和解压缩不出问题
    assert len(decompressed_data) == supposed_decompressed_length
    assert len(zlib.compress(decompressed_data)) == int.from_bytes(one_entry[8:12], byteorder='little')

    with open('./TXTs/'+txt_name, 'w', encoding='utf-8') as f:
        f.write(decompressed_data.decode('shift-jis'))
