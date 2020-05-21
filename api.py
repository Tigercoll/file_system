from fastapi import  APIRouter
from starlette.responses import FileResponse
import os
from settings import BASE_FILE_PATH
from tool import get_dir_size,get_update_time,get_file_size
router = APIRouter()

# 封装返回状态
class StatusData(object):
    def __init__(self,status=200,msg='请求成功',data=None,error=None):
        '''
        :param status: 请求状态,请求成功 200,创建成功201,删除成功204,请求失败400,创建失败401
        :param msg: 信息
        :param data: 数据
        '''
        self.status=status
        self.msg=msg
        self.data=data
        self.error=error
    def to_dict(self):
        return self.__dict__



@router.get('/files/{file_path:path}')
def get_files_list(file_path:str=None):
    status_data = StatusData()
    status_data.data = []
    base_file_path = BASE_FILE_PATH
    # 如果file_path 为空,则查询根目录
    # 如果用 os.path.join() 会出现可以访问任意盘的问题所以这里改用+号
    current_file_path = base_file_path+file_path
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
                status_data.data.append({'name':file,'file_type':'dir','update_time':get_update_time(path),'size':get_dir_size(path)})
            else:
                status_data.data.append({'name': file, 'file_type': 'file','update_time':get_update_time(path),'size':get_file_size(path)})
        return status_data.to_dict()
    # 否则为文件 直接返回FileResponse
    else:
        return FileResponse(current_file_path)