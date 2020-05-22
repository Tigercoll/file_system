import time
import os
# 获取修改时间
def get_update_time(file):
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.path.getmtime(file)))

# 转化size
def change_size(size):
    count = 0
    dic = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB'}
    while size > 1024:
        size = size / 1024
        count += 1
    # 保留两位小数
    return '%.2f %s' % (size, dic[count])

# 获取文件大小
def get_file_size(file):
    size = os.path.getsize(file)
    return change_size(size)

# 获取目录大小,需要用os.walk
def get_dir_size(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return change_size(size)