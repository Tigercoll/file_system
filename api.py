from fastapi import  APIRouter,UploadFile,File
from starlette.responses import FileResponse
from pydantic import BaseModel
import os
import time
import shutil
import traceback
from settings import BASE_FILE_PATH,MOVE,BAK_FILE_PATH
from tool import get_dir_size,get_update_time,get_file_size
router = APIRouter()

# 封装返回状态
class StatusData(object):
    def __init__(self,status=200,msg='请求成功',data=None):
        '''
        :param status: 请求状态,请求成功 200,创建成功201,删除成功204,请求失败400,创建失败401
        :param msg: 信息
        :param data: 数据
        '''
        self.status=status
        self.msg=msg
        self.data=data
    def to_dict(self):
        return self.__dict__


# 获取文件列表
@router.get('/files/{file_path:path}')
def get_files_list(file_path:str=None):
    status_data = StatusData()
    status_data.data = []
    base_file_path = BASE_FILE_PATH
    # 如果file_path 为空,则查询根目录
    # 如果用 os.path.join() 会出现可以访问任意盘的问题所以这里改用+号
    current_file_path = base_file_path+file_path
    try:
        if not os.path.exists(current_file_path):
            status_data.status=402
            status_data.msg = '文件或文件夹不存在'
            status_data.error = '路径错误'
            return status_data.to_dict()

        if not file_path or os.path.isdir(current_file_path):
            base_files_list = os.listdir(current_file_path)
            for file in  base_files_list:
                # 拼接成完整路径
                path = os.path.join(current_file_path,file)
                # 判断文件是否为目录
                if  os.path.isdir(path):
                    # 把文件夹放在前面
                    status_data.data.insert(0,{'name':file,'file_type':'dir','update_time':get_update_time(path),'size':get_dir_size(path)})
                else:
                    status_data.data.append({'name': file, 'file_type': 'file','update_time':get_update_time(path),'size':get_file_size(path)})
            return status_data.to_dict()
        # 否则为文件 直接返回FileResponse
        else:
            return FileResponse(current_file_path)
    except Exception as e:
        status_data.status=500
        status_data.msg=traceback.format_exc()
        return status_data.to_dict()


class FolderItem(BaseModel):
    name:str
    new_name:str=None
# 添加文件夹 重命名
@router.post('/files/{file_path:path}')
def add_folder(folder_item:FolderItem,file_path:str=None):
    status_data = StatusData()
    base_file_path = BASE_FILE_PATH
    current_file_path = base_file_path + file_path
    try:
        # 判断是否有new_name,有则为重命名
        if folder_item.new_name:
            # 判断重命名文件夹是否已存在
            if not os.path.exists(os.path.join(current_file_path, folder_item.new_name)):
                os.rename(os.path.join(current_file_path,folder_item.name),os.path.join(current_file_path,folder_item.new_name))
                # 如果用程序改名的时候不会更新修改时间,这里我们调用os.utime 更改
                os.utime(os.path.join(current_file_path,folder_item.new_name),(time.time(),time.time()))
                status_data.status = 201
                status_data.msg = '重命名成功'
            else:
                status_data.status = 401
                status_data.msg = '文件夹已存在'
        # 判断文件夹是否存在
        else:
            if not os.path.exists(os.path.join(current_file_path,folder_item.name)):
                os.mkdir(os.path.join(current_file_path,folder_item.name))
                status_data.status=201
                status_data.msg='创建成功'

            else:
                status_data.status=401
                status_data.msg='文件夹已存在'
        return status_data.to_dict()
    except Exception as e:
        status_data.status = 500
        status_data.msg = traceback.format_exc()
        return status_data.to_dict()

# 上传文件
@router.post('/upload/{file_path:path}')
async def create_upload(file_path:str=None,file:UploadFile=File(...)):
    base_file_path = BASE_FILE_PATH
    status_data = StatusData()
    try:
        contents = await file.read()
        with open(os.path.join(base_file_path,file_path,file.filename), 'wb') as f:
            f.write(contents)
            status_data.status=200
            status_data.msg='上传成功'
        return status_data.to_dict()
    except Exception as e:
        status_data.status = 500
        status_data.msg = traceback.format_exc()
    return status_data.to_dict()

# 删除文件或目录
@router.delete('/files/{file_path:path}')
def del_files(file_path:str):
    #不允许为空,为空则删除跟目录了
    status_data = StatusData()
    base_file_path = BASE_FILE_PATH
    current_file_path = base_file_path + file_path
    try:
        # 如果为目录则计算他的大小
        if os.path.isdir(current_file_path):
            if get_dir_size(current_file_path)=='0.00 B':
                if not MOVE:
                    shutil.rmtree(current_file_path)
                else:
                    # 移动前判断是否存在
                    _, file_name = os.path.split(current_file_path)
                    if os.path.exists(os.path.join(BAK_FILE_PATH,file_name)):
                        bak = f'_{time.time()}_bak'
                        # 存在则加上.bak
                        os.rename(current_file_path,current_file_path+bak)
                        current_file_path=current_file_path+bak
                    shutil.move(current_file_path,BAK_FILE_PATH)
                status_data.status=204
                status_data.msg='删除成功'
            else:
                status_data.status=400
                status_data.msg='此目录不为空,不能删除'
        else:
            if not MOVE:
                shutil.rmtree(current_file_path)
            else:
                _,file_name=os.path.split(current_file_path)
                if os.path.exists(os.path.join(BAK_FILE_PATH,file_name)):
                    bak = f'_{time.time()}_bak'
                    # 存在则加上.bak
                    os.rename(current_file_path, current_file_path + bak)
                    current_file_path = current_file_path + bak
                shutil.move(current_file_path, BAK_FILE_PATH)
            status_data.status = 204
            status_data.msg = '删除成功'
        return  status_data.to_dict()
    except Exception as e:
        status_data.msg=traceback.format_exc()
        status_data.status=500
        return status_data.to_dict()


from typing import List
# 移动或者粘贴文件
class CopyOrMoveItem(BaseModel):
    item_list:List
    item_type:str

def copy_dir(src,dest):
    # 目录是否存在
    if not os.path.exists(dest):
        os.mkdir(dest)
    src_list = os.listdir(src)
    for item in src_list:
        # 如果是目录就递归
        if os.path.isdir(os.path.join(src,item)):
            copy_dir(os.path.join(src,item),os.path.join(dest,item))
        else:
            shutil.copy(os.path.join(src,item),dest)



@router.post('/moveorcopy/{file_path:path}')
def move_or_copy(copy_or_move_item:CopyOrMoveItem,file_path:str=None):
    status_date = StatusData()
    print(11)
    # 判断是移动还是粘贴
    try:
        if copy_or_move_item.item_type=='move':
            for item in copy_or_move_item.item_list:
                # 判断文件或文件夹是否已存在
                _,file_name = os.path.split(item)
                if os.path.exists(BASE_FILE_PATH+file_path+file_name):
                # 存在就报错
                    raise Exception(file_name+'已存在')
                shutil.move(BASE_FILE_PATH+item,BASE_FILE_PATH+file_path)
            status_date.msg='移动成功'
        elif copy_or_move_item.item_type=='copy':
            # 复制分两种,一种是文件,一种是目录
            for item in copy_or_move_item.item_list:
                _, file_name = os.path.split(item)
                if os.path.exists(BASE_FILE_PATH  + file_path + file_name):
                    # 存在就报错
                    raise Exception(file_name + '已存在')
                if os.path.isfile(BASE_FILE_PATH+item):
                    # 文件就直接复制
                    shutil.copy(BASE_FILE_PATH+item,BASE_FILE_PATH+file_path)
                else:
                    # 文件的话就要递归复制
                    copy_dir(BASE_FILE_PATH+item,BASE_FILE_PATH+file_path+file_name)
            status_date.msg='粘贴成功'
    except Exception as e:
        print(traceback.format_exc())
        status_date.msg=str(e)
        status_date.status=500
    return status_date.to_dict()