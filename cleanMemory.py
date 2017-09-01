#coding=utf-8
"""
Create On 2017/9/1

@author: Ron2
"""

import time
import commands

class CleanMemory(object):
    """
    这个脚本用来清理内存.请用sudo执行
    """
    def __init__(self):
        pass


    def start(self, intervalTime=60 * 30):
        """
        开始清理
        :param intervalTime:            执行间隔
        :return: 
        """
        while True:
            now = int(time.time())
            if now / intervalTime == 0:
                a, b = commands.getstatusoutput("sync; echo 3 | tee /proc/sys/vm/drop_caches")
                print a, b

            time.sleep(1)


if __name__=="__main__":
    """
    """
    obj = CleanMemory()
    obj.start(3)



