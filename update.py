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
def writeUpgrade(exename):
    b = open("upgrade.py",'w')
    TempList = "# coding=UTF-8\n\n"
    TempList += "import os\n"
    TempList += "import time\n"
    TempList += "import subprocess\n"
    TempList += "import paramiko\n\n"
    TempList += "os.remove(os.getcwd()+'\\"+exename+"')\n"
    TempList += "ssh = paramiko.Transport(('10.12.192.62',22))\n"
    TempList += "ssh.connect(username='cmy', password='cmy')\n"
    TempList += "stfp = paramiko.SFTPClient.from_transport(ssh)\n"
    TempList += "stfp.get('/home/cmy/atc/Personal_Folder/CMY/WPAutotest/"+exename+"','"+ os.getcwd()+"\\"+exename+"')\n"
    TempList += "stfp.close()\n"
    TempList += "ssh.close()\n"
    TempList += "time.sleep(2)\n"
    TempList += "os.system('start " + exename +"')"
    b.write(TempList)
    b.close()
    subprocess.Popen("python upgrade.py") #不显示cmd窗口
    sys.exit()
    #如果是FTP就编写FTP的相应代码

def checkVersion(): #检查版本
    if not is_company_network():
        print('连接公司内网后进行更新')
    if not os.path.isdir('z:\\'):  #判断是否有z盘，没有就mount，使用mount命令需要提前安装好NFS客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        ssh.connect(hostname ='10.12.192.62' , port=22, username='cmy', password='cmy')
        stdin, stdout, stderr = ssh.exec_command('cat ~/atc/Personal_Folder/CMY/WPAutotest/version.ini')
        newversion = stdout.read().decode()[18:]
    return newversion

