#!/bin/bash

echo $1

# if [ "$1" = "-r" ]
# then
#     echo "重启redis..."
#     sh redis_stop.sh
# fi

cd ../
sudo python cleanMemory.py &
ps -ef | grep cleanMemory
echo "启动清理内存脚本成功..."

