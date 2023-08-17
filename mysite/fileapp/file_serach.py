import os
import re

def get_files_without_numbers(folder_path):
    file_list = []
    for filename in os.listdir(folder_path):
        if not re.search(r'\d', filename):  # 使用正则表达式匹配文件名中是否含有数字
            file_list.append(filename)
    return file_list

if __name__=="__main__":
    folder_path = 'mysite/fileapp/file_data/outcome_alldata'  # 替换为你的文件夹路径
    files = get_files_without_numbers(folder_path)
    print(files)