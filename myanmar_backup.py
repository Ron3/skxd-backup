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
MYANMAR_TEM_PATH = "/data/backup/ron"


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
    # yesterdayZeroClockTime = zeroClockTime - 24 * 3600
    print "zeroClockTime => ", zeroClockTime

    ''' 因为备份脚本在凌晨启动.也就是找到最近那个备份.然后传过去他们的S3 '''
    resultFileNameArray = []
    for fileName in backupZipFileArray:
        if os.path.getctime(fileName) >= zeroClockTime and fileName.rfind(".zip") != -1:
            print "filePath => ", fileName
            resultFileNameArray.append(fileName)

    return resultFileNameArray


def _syncToMyanmar(resultFileNameArray):
    """
    同步给缅甸
    :param resultFileNameArray:
    :return:
    """
    if resultFileNameArray == None or len(resultFileNameArray) <= 0:
        return

    try:
        ''' 要把原来的先掉 '''
        command = "rm -rf %s" % MYANMAR_TEM_PATH
        resultCode, result = commands.getstatusoutput(command)
    except:
        pass

    ''' 1, 首先得到今天的时间.然后去建立1个文件夹.最终得到这样的路径 ron/2017-01-24 '''
    todayText = str(datetime.datetime.now())[0:10]
    todayPath = os.path.join(MYANMAR_TEM_PATH, todayText)

    # ''' 2, 然后在建立1个叫gamedata的目录. '''
    # fianlPath = os.path.join(todayPath, "gamedata")
    # print "final Path ==> ", fianlPath

    ''' 2, 这里开始.根据服务器id来创建目录.把文件都放到对应的目录下 '''
    finalPathDic = {}
    for fileName in resultFileNameArray:
        serverId = _getServerIdByFileName(fileName)
        if serverId == None:
            continue

        try:
            fianlPath = os.path.join(todayPath, serverId)
            finalPathDic[fileName] = fianlPath
            os.makedirs(fianlPath)
        except:
            pass

    ''' 3, 执行shell 命令.将文件copy到目录 '''
    for fileName in resultFileNameArray:
        try:
            fianlPath = finalPathDic.get(fileName)
            if fianlPath == None:
                continue

            command = "cp %s %s" % (fileName, fianlPath)
            print "command =>", command
            resultCode, result = commands.getstatusoutput(command)
        except:
            traceback.print_exc()

    ''' 4, 同步去缅甸的服务器 '''
    command = "rsync -avz %s rsync://backup-storage.squargame.com/MyCombo_Database/" % (todayPath, )
    print "command =>", command
    resultCode, result = commands.getstatusoutput(command)

    try:
        ''' 5, 最终删掉 '''
        command = "rm -rf %s" % MYANMAR_TEM_PATH
        resultCode, result = commands.getstatusoutput(command)
    except:
        pass


def _getServerIdByFileName(fileName):
    """
    从文件名字.得到serverId
    :param fileName:
    :return:
    """
    # /data/backup/redis_by_date/20170217_2003_bpsg.rdb.zip
    if fileName == None or len(fileName) <= 0:
        return None

    index = fileName.rfind("_bpsg.rdb.zi")
    if index < 0:
        return None

    return fileName[index-4 :index]






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

    ''' 4, 把文件放到某个目录下.然后rsync过去 '''
    ''' rsync -avz /data/backup/redis_by_date/2017-01-24  rsync://backup-storage.squargame.com/MyCombo_Database/ '''
    ''' redis_by_date/2017-01-24/gamedata/20170124_2000_bpsg.rdb.zip  '''
    ''' 要这么放.然后他会把gamedata/20170124_2000_bpsg.rdb.zip 整个目录传递过去 '''
    ''' 到了他们那边.他们则是存在这样的目录下 2017-01-24/gamedata/20170124_2000_bpsg.rdb.zip '''
    _syncToMyanmar(resultFileNameArray)





    # ''' 4, 把文件弄过去 '''
    # for fileName in resultFileNameArray:
    #     try:
    #         command = "scp %s bpsg@%s:/data/backup_redis_data/" % (fileName, serverIP)
    #         print "command =>", command
    #         resultCode, result = commands.getstatusoutput(command)
    #         print "resultCode, result=> ", resultCode, result
    #     except:
    #         traceback.print_exc()





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






