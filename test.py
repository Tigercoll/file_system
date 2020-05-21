import os
import time
stinfo = os.stat(r'D:/files_test/')
print(stinfo)
# os.utime(r'D:/files_test/',(time.time(),time.time()))