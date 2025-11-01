import os
import zlib
assert os.path.exists('./TXTs'), '必须在 TXTs 文件夹下放置相应的 .txt 文件！'
def pad_to_multiple_of_16(binary_str):
    remainder = len(binary_str) % 16
    if remainder != 0:
        binary_str += 0x00.to_bytes(16 - remainder)
    return binary_str

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

compressed_blocks = []
entries = []
txt_names = b""
compress_offset = 0x20
# 主体数据
for filename in os.listdir('./TXTs'):
    original_data = open('./TXTs/'+filename, 'r', encoding='utf-8').read().encode('shift-jis')
    compress_data = zlib.compress(original_data)

    one_entry = b''
    one_entry += len(txt_names).to_bytes(4, byteorder='little')
    one_entry += compress_offset.to_bytes(4, byteorder='little')
    one_entry += len(compress_data).to_bytes(4, byteorder='little')
    one_entry += 0x20.to_bytes(4, byteorder='little')
    one_entry += len(original_data).to_bytes(4, byteorder='little')
    one_entry += 0x00.to_bytes(4, byteorder='little')
    entries.append(one_entry)

    txt_names += filename.encode('ascii') + b'\x00'

    compress_data = pad_to_multiple_of_16(compress_data)
    assert len(compress_data) % 16 == 0

    compress_offset += len(compress_data)
    compressed_blocks.append(compress_data)

compress_block_total_length = 0
for block in compressed_blocks:
    compress_block_total_length += len(block)
assert compress_block_total_length % 16 == 0

# 文件头
head = b''
head += b'ARC '
head += len(entries).to_bytes(4, byteorder='little')
head += 0x00.to_bytes(4, byteorder='little')
head += (0x20 + compress_block_total_length).to_bytes(4, byteorder='little')
head += (0x20 + compress_block_total_length + len(entries) * 24).to_bytes(4, byteorder='little')
head += len(txt_names).to_bytes(4, byteorder='little')
head += 0x00.to_bytes(8, byteorder='little')

with open('script.arc', 'wb') as f:
    f.write(head)
    for block in compressed_blocks:
        f.write(block)
    for entry in entries:
        f.write(entry)
    f.write(txt_names)