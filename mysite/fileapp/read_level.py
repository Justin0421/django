import pandas as pd
import numpy as np
import time
import os
import shutil
from django.conf import settings
import csv


# 清理
# 读取txt文件，剔除txt中“---”
def clean_txt(filename):
    #逐行读取，写入列表 
    clean_str= ['-------------------------------------------------------------\n']
    with open(filename,"r") as file:
        lines = []
        for i in file:
            if i not in clean_str:
                lines.append(i)
    #写入新文件，并返回路径
    filenew = filename[0:len(filename)-4] + "清理.txt"
    file_write = open(filenew,'w')
    for i in lines:
        file_write.writelines(i)
    file_write.close()
    return(filenew)

# pandas读取txt
def loadtxtmethod_pd(filename):
    data = pd.read_csv(filename,delimiter='|')
    return data

# pandas数据清理：转点、视距、读数，去重、仅保留无重复的测点编号和对应高程;
def clean_pd(filenew):
    # 读取至dataframe对象
    data = loadtxtmethod_pd(filenew)

    #删除中间文件，，注意注意
    os.remove(filenew)
    # 增加日期属性，将高程列名改为监测日期
    filedate = filenew[-24:-14]
    filetime = filenew[-13:-8]
    print(filedate,filetime)

    #修改列名
    data.rename(columns = {'测点                ':'测点编号',
                                  '视距          ':'视距',
                                  '读数      ':'读数',
                                  '高程                ':filedate}, inplace = True)

    data.shape
    data.info()
    data.dtypes
    print(data.index)
    print(data.columns)
    # data.describe()

    # 清洗空格
    print(data.values)
    # 对整张表格去空格
    # data.replace('\s+','',regex=True,inplace=True)
    # 对第二列去空格
    data.iloc[:,1] = data.iloc[:,1].str.strip()
    print(data.values)

    #提取测点和高程列
    df1 = data[['测点编号',filedate]]
    print(df1.values)

    # 去除转点行
    df2 = df1[df1['测点编号'] != 'ZD']
    print(df2)

    # 去除重复行
    df2.duplicated()
    df3 = df2.drop_duplicates().sort_values('测点编号')

    # 建立索引，去除0开始的索引列
    df3.set_index('测点编号', inplace=True) # 建立索引并生效

    print(df3)

    # 存储为CSV格式
    file_csv = filenew[0:len(filenew)-4]+'.csv'
    print(file_csv)
    df3.to_csv(file_csv, encoding = 'utf_8_sig')
    return(file_csv)


    # df3 = df2.drop_duplicates(['测点                '])   #对特定列去重
    #   norepeat_df = df.drop_duplicates(subset=['A_ID', 'B_ID'], keep='first')
    #上面的命令去掉UNIT_ID和KPI_ID列中重复的行，并保留重复出现的行中第一次出现的行
    # 补充： 
    # 当keep=False时，就是去掉所有的重复行 
    # 当keep=‘first’时，就是保留第一次出现的重复行 
    # 当keep=’last’时就是保留最后一次出现的重复行。 
    #  （注意，这里的参数是字符串，要加引号！！！）


# 下一步，将该日期的监测数据写入数据库

def data_join(file_csv, data_table):
    
    # 时间转字符串
    formatted_date = time.strftime("%Y-%m-%d %H.%M", time.localtime())
    print(formatted_date)
    # 备份的总表路径
    backup_table=data_table[0:len(data_table)-4]+ formatted_date + '.csv'
    print(backup_table)

    # 读取本次监测数据
    pd_data = pd.read_csv(file_csv,delimiter=',')
    pd_data.set_index('测点编号', inplace=True) # 建立索引并生效
    print(pd_data)
    
    # 读取表格，已有则先备份一份带时间戳；再合并；再覆盖写入源总表
    # 没有则新建，直接复制进去；
    if os.path.exists(data_table):
        print(f"The file '{data_table}' exists.")
        pd_all = pd.read_csv(data_table,delimiter=',')
        pd_all.to_csv(backup_table,index = False,  encoding = 'utf_8_sig')  
        print("总表备份完毕")
        result = pd.merge(pd_all, pd_data, on = '测点编号', how = 'outer')
        # # 建立索引，去除0开始的索引列
        # result.set_index('测点编号', inplace=True) # 建立索引并生效
        result.to_csv(data_table,index = False, encoding = 'utf_8_sig')
        print('合并完毕')
    else:
        print(f"The file '{data_table}' does not exist.")
        shutil.copyfile(file_csv,data_table)
        print("新建总表完毕")
    
    # print(pd_all)
    # if pd_all.empty:
    #     print("CSV 文件为空")
    #     # 复制数据
    #     pd_data.to_csv(newdata_table,index = False,  encoding = 'utf_8_sig')  
    #     print("复制完毕")
    # else:
    #     print("CSV 文件不为空")
    #     # 合并，保留全部数据
    #     result = pd.merge(pd_all, pd_data, on = '测点编号', how = 'outer')
    #     # # 建立索引，去除0开始的索引列
    #     # result.set_index('测点编号', inplace=True) # 建立索引并生效
    #     result.to_csv(newdata_table,index = False, encoding = 'utf_8_sig')
    #     print('合并完毕')


#处理平台上传的txt文件
def handle_uploaded_file(file):
    filePath = os.path.join('mysite/fileapp/file_data/',file.name) 
    with open(filePath, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    # 读取txt，清理并写入新txt
    filenew = clean_txt(filePath)

    # pandas读取并清理数据
    file_csv = clean_pd(filenew)
    
    # 将该次监测数据并入整体数据
    data_table = os.path.join('mysite/fileapp/file_data/outcome_alldata/',file.name[0:-22]+'.csv') 

    data_join(file_csv, data_table) 

if __name__=="__main__":
    # 读取清单，批量处理
    #filelist = 

    filename = '/home/huang/dataprocess/data_process/彩虹桥站-中山八站2022-08-17 13.07数据.txt'

    # 读取txt，清理并写入新txt
    filenew = clean_txt(filename)

    # pandas读取并清理数据
    file_csv = clean_pd(filenew)
    
    # 将该次监测数据并入整体数据
    data_table = '/home/huang/dataprocess/data_process/彩虹桥站-中山八站-数据.csv'
    data_join(file_csv, data_table) 

    #按需添加其他格式