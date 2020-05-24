import os
import time
# stinfo = os.stat(r'D:/files_test/')
# print(os.path.join(r'D:/files_test/','','1.txt'))
# print(stinfo)
# os.utime(r'D:/files_test/',(time.time(),time.time()))
import requests

data = {
    'item_list': ["111/新建 文本文档.txt"],
    'item_type': "copy"
}
res = requests.post('http://127.0.0.1:3000/api/private/v1/move_or_copy/')
print(res.text)