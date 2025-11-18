# BARON_Engine_Tools

script_unpack.py
用于解包命名为script.arc的脚本文件

script_pack.py
用于封包命名为script.arc的脚本文件

image_unpack.py
用于解包image.arc的文件

解包封包方法同理把script.arc文件和script_unpack.py/script_pack.py放入同一个根目录，点击script_unpack.py/script_pack.py

00_skip=^//

10_skip=^(@|BG|CHR|VOICE|SOUND|CHR_OFF|BG_COLOR|FADE_OUT|MENU_CLEAR|MENU_CHOICE|goto|:S_|:L_|FADE_OUT|BG_COLOR|MUSIC|SET_SFLAG|G_).*

15_skip=^MENU chapter

20_search=^NAME\s+"?(?P<name>[^"\r\n]+)"?$

30_search=^MENU\s+S_\d+[ab]\s+"(?P<msg>[^"\r\n]+)"$

40_search=^(?P<msg>「[^」]*」)$

50_search=^(?P<msg>[^A-Za-z\r\n]+)$







