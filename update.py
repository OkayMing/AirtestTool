# coding=UTF-8
import os
import sys
import socket
import paramiko
import subprocess
import configparser


# 用IP的开头判断是否出差在外
def is_company_network():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = ("8.8.8.8", 80)
        s.connect(address)
        sockname = s.getsockname()
        ip = sockname[0]
        port = sockname[1]
    finally:
        s.close()
        
    if ip.startswith('10.12'):
        return True
    
    return False


#编写bat脚本，删除旧程序，运行新程序
def writeUpgrade(exe_name):
    #b = open("upgrade.bat",'w')
    b = open("upgrade.py",'w')
    #TempList = "@echo off\n"
    '''TempList = "ssh cmy@10.12.192.62\n"  #判断是否有新版本的程序，没有就退出更新。
    TempList += "timeout /t 2 /nobreak\n"  #等待2秒
    TempList += "cmy\n"
    TempList += "timeout /t 10 /nobreak\n"  #等待10秒
    TempList += "del " + os.path.realpath(exe_name) + "\n" #删除旧程序
    TempList += "copy  z:\\" + exe_name + " " + exe_name + '\n' #复制新版本程序
    TempList += "echo 更新完成，正在启动...\n"
    TempList += "timeout /t 3 /nobreak\n"
    TempList += "start " + exe_name + '\n'   #"start 1.bat\n"
    TempList += "exit"'''
    TempList = "# coding=UTF-8\n\n"
    TempList += "import os\n"
    TempList += "import paramiko\n\n"
    TempList += "os.remove(os.getcwd()+'\Autotest.exe')\n"
    TempList += "ssh = paramiko.Transport(('10.12.192.62',22))\n"
    TempList += "ssh.connect(username='cmy', password='cmy')\n"
    TempList += "stfp = paramiko.SFTPClient.from_transport(ssh)\n"
    TempList += "stfp.get('/home/cmy/atc/Personal_Folder/CMY/WPAutotest/Autotest.exe',os.getcwd()+'\Autotest.exe')\n"
    TempList += "stfp.close()\n"
    TempList += "ssh.close()\n"
    b.write(TempList)
    b.close()
    subprocess.Popen("python upgrade.py") #不显示cmd窗口
    #os.system('start upgrade.bat')  #显示cmd窗口
    #如果是FTP就编写FTP的相应代码

def checkVersion(): #检查版本
    if not is_company_network():
        print('连接公司内网后进行更新')
    if not os.path.isdir('z:\\'):  #判断是否有z盘，没有就mount，使用mount命令需要提前安装好NFS客户端
        server_path = f'\\\\10.12.192.62\home\cmy\\atc\Personal_Folder\CMY\WPAutotest'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        ssh.connect(hostname ='10.12.192.62' , port=22, username='cmy', password='cmy')
        stdin, stdout, stderr = ssh.exec_command('cat ~/atc/Personal_Folder/CMY/WPAutotest/version.ini')
        newversion = stdout.read().decode()[18:]
        #print(newversion)
        #config = configparser.ConfigParser()  # 类实例化
        #config.read(versioninfo)
        #value = config['select']['version'] #获取版本号
        #print(value)
    #path = f'{server_path}\\version.ini'
    #print(path)
    #config.read(path)
    #value = config['select']['version'] #获取版本号
    #print(value)
    return newversion
    #也可以使用以下代码获取程序版本号
    #url = r'http://172.18.114.172/index.html'
    #value = requests.get(url).text
