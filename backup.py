#coding=utf-8
"""
Create On 16/9/12

@author: Ron2
"""


import sys
import getopt
import random
from optparse import OptionParser
import time
import datetime
import re
import traceback
import commands
import os
import os.path


''' 路径大家都统一.可以直接在这里配置 '''
BACKUP_PATH = "/data/backup/redis_by_date/"
# BACKUP_PATH = "/Users/Ron2/MyMovie"



def _getTodayZeroClockTime():
    """
    获取今天凌晨0点的时间
    :return:
    """
    now = datetime.datetime.now()
    date = now.date()
    zeroClock = time.mktime(date.timetuple())
    return zeroClock




def _findTodayBackFile():
    """
    找到今天备份的文件
    :return:
    """
    global BACKUP_PATH
    rootDir = BACKUP_PATH

    fileList = os.listdir(rootDir)

    ''' 遍历得到所有. '''
    backupZipFileArray = []
    for fileName in fileList:
        filePath = os.path.join(rootDir, fileName)
        if os.path.isdir(filePath):
            continue
        else:
            backupZipFileArray.append(filePath)

    ''' 找到是今天创建的 && 正则表示式匹配的 '''
    zeroClockTime = _getTodayZeroClockTime()
    print "zeroClockTime => ", zeroClockTime

    resultFileNameArray = []
    for fileName in backupZipFileArray:
        if os.path.getctime(fileName) >= zeroClockTime and fileName.rfind(".zip") != -1:
            print "filePath => ", fileName
            resultFileNameArray.append(fileName)

    return resultFileNameArray



def backupData(serverIP, hour):
    """
    将文件传输到指定的服务器里面去
    :param serverIP:                存储备份的服务器
    :param hour:                    从现在开始.多少小时以内均可以
    """
    ''' 1, 求出传输时间点.随机一个值是为了所有服务器错开时间点传过去 '''
    deltaTime = random.randint(0, hour * 3600+1)
    now = time.time()
    copyTime = now + deltaTime

    ''' 2, 一直等到传输时间 '''
    while copyTime >= time.time():
        time.sleep(1)

    ''' 3, 找到今天备份的 '''
    resultFileNameArray = _findTodayBackFile()
    if resultFileNameArray is None:
        return

    ''' 4, 把文件弄过去 '''
    for fileName in resultFileNameArray:
        try:
            command = "scp %s bpsg@%s:/data/backup_redis_data/" % (fileName, serverIP)
            print "command =>", command
            resultCode, result = commands.getstatusoutput(command)
            print "resultCode, result=> ", resultCode, result
        except:
            traceback.print_exc()





if __name__=="__main__":
    """
    备份
    """
    parser = OptionParser(usage="usage:%prog [optinos] filepath")
    parser.add_option("-s", "--server",
                      action="store",
                      type="string",
                      dest="server",
                      default="10.8.16.64",         # HK MySQL服务器默认的内网IP
                      help="target server ip"
                      )

    parser.add_option("-t", "--timeHour",
                      action="store",
                      type='int',
                      dest="timeHour",
                      default=4,
                      help="Specify if the target is an URL"
                      )

    (options, args) = parser.parse_args()

    print "targetServerIp =>", options.server
    print "hour => ", options.timeHour
    backupData(options.server, int(options.timeHour))






