import zlib
import os

data = open('image.arc', 'rb').read()

"""
image.arc 本质上是若干个图片文件整合起来的，整个文件的结构为：
1. 头 0x20 字节：文件头
2. 之后的主体：图片文件数据，每个图片文件与 3. 中的条目一一对应
3. 之后的一小段：若干个条目，表示这些图片文件的一些信息，一个条目为 24 字节，固定结构
4. 最后的明文部分：图片文件名，每个文件名与 3. 中的条目一一对应

文件头结构：
0x00~0x04: 0x41524320 ("ARC ")
0x04~0x08: 图片文件个数，即 3. 中的条目个数，乘以 24 （每个条目的字节长度）后即所有条目的总长度
0x08~0x0C: 未知，但似乎填零没影响
0x0C~0x10: 3. 开始的偏移地址
0x10~0x14: 4. 开始的偏移地址
0x14~0x18: 4. 的总长度
0x18~0x20：填零

3. 中 24 字节条目的结构：
0x00~0x04：条目对应的图片文件名在 4. 中的偏移
0x04~0x08：条目对应的图片文件数据块在 image.arc 中的偏移地址
0x08~0x0C：图片的大小
0x0C~0x10：未知，但其值似乎固定为 0x20
0x10~0x14：因为图片没有压缩，所以这一项是 0
0x14~0x18：未知，但实测填零没有影响
"""

assert data[:4] == b'ARC '
num_IMAGE = int.from_bytes(data[4:8], byteorder='little')
offset_entry = int.from_bytes(data[12:16], byteorder='little')
offset_image_name = int.from_bytes(data[16:20], byteorder='little')

entry_data = data[offset_entry : offset_entry + 24 * num_IMAGE]
image_name_data = data[offset_image_name:]

if not os.path.exists('./IMAGEs'):
    os.mkdir('./IMAGEs')
for i in range(num_IMAGE):
    one_entry = entry_data[i * 24 : (i+1) * 24]

    # 图片文件名
    image_name = image_name_data[int.from_bytes(one_entry[:4], byteorder='little'):].split(b'\x00')[0].decode('utf-8')
    # 图片文件数据
    image_data = data[int.from_bytes(one_entry[4:8], byteorder='little') : int.from_bytes(one_entry[4:8], byteorder='little') + int.from_bytes(one_entry[8:12], byteorder='little')]

    with open('./IMAGEs/'+image_name, 'wb') as f:
        f.write(image_data)
