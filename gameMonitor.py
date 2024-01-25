import os
import re
import sys
import configparser
import time

currentPath = os.getcwd()

# 默认间隔时间，定时执行
interval = 0
# 检测进程名称
processName = ""
# 满足条件执行的命令
command = ""
# 用户
userName = ""
# 内存阈值
memThreshold = 0

def exec_command(exec_str, path = ""):
    cur_paht = os.getcwd()
    if sys.platform.startswith('win') :
        os.chdir(path)
        print(os.getcwd())
        code = os.system(exec_str)
        os.chdir(cur_paht)
        print(os.getcwd())
        return code
    
    print_log(exec_str)
    os.system(exec_str)
    return 0

def print_log(str):
    # 将时间戳转换为日期时间格式
    local_time = time.localtime(time.time())
    str = "[" + time.strftime("%Y-%m-%d %H:%M:%S", local_time) + "] " + str
    print(str)
    return os.system("echo \"" + str + "\"  >> %s/log.log" % currentPath)

def read_config():
    global config
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    global interval, processName, command, userName, memThreshold
    InInterval = config.get('Data', 'interval')
    InProcessName = config.get('Data', 'processName')
    InCommand = config.get('Data', 'command')
    InuserName = config.get('Data', 'userName')
    InMemThreshold = config.get('Data', 'memThreshold')

    if (InInterval != interval or
        InProcessName != processName or
        InCommand != command or
        InuserName != userName or
        InMemThreshold != memThreshold):

        interval = InInterval
        processName = InProcessName
        command = InCommand
        userName = InuserName
        memThreshold = InMemThreshold
        print_log("---- 配置信息已更新")
        print_log("interval : %s" % interval)
        print_log("processName : %s" % processName)
        print_log("command : %s" % command)
        print_log("userName : %s" % userName)
        print_log("memThreshold : %s" % memThreshold)
        print_log("---- 配置信息打印完成")

def KillProcess():
    processids = []
    
    # 打印进程ID
    exec_command("ps -ef | grep PalServer > processInfo.txt")
    processFile = open("processInfo.txt", 'r', encoding='utf-8')
    processLines = processFile.readlines()
    processFile.close()
    for processLine in processLines:
        # 使用正则表达式将多个空格替换为一个空格
        processLine = re.sub(r"\s+", " ", processLine)
        indexOne = processLine.find(" ")
        indexTwo = processLine.find(" ", indexOne + 1)
        processid = processLine[indexOne + 1:indexTwo]
        processids.append(processid)

    # kill进程
    for processid in processids:
        exec_command("kill -9 %s" % processid)

def findIndex(str, targetStr, number):
    currentIndex = 0
    currentNum = 0
    while(1) :
        currentIndex = str.find(targetStr, currentIndex)
        
        if(currentIndex == -1) :
            return -1
        
        currentNum = currentNum + 1
        if (currentNum == number) :
            return currentIndex
        
        currentIndex = currentIndex + 1

if __name__ == '__main__':
    os.system("echo \"\" > log.log")

    # 处理路径拼接异常的问题
    os.system("git config --global core.quotepath false")

    while(1) :
        read_config()

        os.system("top -b -n 1 > file.txt")
        file = open("file.txt", 'r', encoding='utf-8')
        lines = file.readlines()
        file.close()
        bFind = False

        # 检测进程是否存在
        for line in lines:
            # 将字符串转换成列表
            processNames = processName.split(',')
            bFindProcess = False
            for process in processNames :
                if(line.find(process) != -1):
                    bFindProcess = True
                    break

            if (line.find(userName) != -1 and bFindProcess) :
                if (bFind) :
                    print_log("检测到多个进程，杀掉全部进程重启")
                    KillProcess()
                    bFind = False
                else :
                    bFind = True
                    # 使用正则表达式将多个空格替换为一个空格
                    line = re.sub(r"\s+", " ", line)
                    # print_log(line)

                    indexOne = findIndex(line, " ", 10)
                    indexTwo = findIndex(line, " ", 11)
                    mem = line[indexOne + 1:indexTwo]
                    # 字符串转换为数字
                    if(float(mem) > float(memThreshold)):
                        print_log("大于阈值 当前：" + str(mem) + " 阈值：" + str(memThreshold))

                        # 杀掉进程
                        KillProcess()

                        bFind = False
                    else:
                        print_log("小于阈值 当前：" + str(mem) + " 阈值：" + str(memThreshold))

                    os.system("swapon --show > swapon.txt")
                    file = open("swapon.txt", 'r', encoding='utf-8')
                    lines = file.readlines()
                    file.close()
                    print_log("打印交换分区：" + str(lines[1]))


        if(bFind == False) :
            # 没找到进程，执行命令
            print_log("进程不存在，执行命令重新拉起进程")
            print_log("打印所有进程：\n" + str(lines))
            exec_command(command)
            print_log("进程已拉起")

        # 每分钟检测一次
        time.sleep(int(interval))
