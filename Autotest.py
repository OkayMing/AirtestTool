# -*- coding: utf-8 -*-
import re
import os
import sys
import subprocess
import time
from PyQt5.QtWidgets import QAbstractItemView,QApplication,QTextBrowser,QHBoxLayout,QPushButton,QTreeWidget,QWidget,QFileDialog,QTreeWidgetItem,QVBoxLayout
from PyQt5.QtCore import Qt,QThread,pyqtSignal,QSize
from PyQt5.QtGui import QGuiApplication




class Runtask(QThread):
    textSignal = pyqtSignal(str)
    resultSignal = pyqtSignal(str)
    stateSignal = pyqtSignal(int)
    def __init__(self,rootpath):
        super(Runtask,self).__init__()
        self.rootpath = rootpath


    def stop(self):
        os.system('taskkill /t /f /pid {}'.format(self.p.pid))


    def run(self):
        Item_list = []
        count = self.rootpath.childCount()
        if count !=0:
            for i in range(count):
                item = self.rootpath.child(i)
                if item.checkState(0) == Qt.Checked:
                    Item_list.append(item.text(0))
        for i in Item_list:
            self.p = subprocess.Popen('python -m airtest run ' + self.rootpath.text(0)+ '/' + i +' --device Windows:///',shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,encoding = 'gbk',start_new_session=True)
            while True:
                buff = self.p.stdout.readline()
                if buff != '':
                    self.textSignal.emit(buff)
                if buff.find('FAILED') != -1 :
                    self.textSignal.emit('************************' + i + ' 测试失败****************************')
                    self.resultSignal.emit(i + ' is FAILED')
                    break
                elif buff.find('OK') != -1:
                    self.textSignal.emit('************************' + i + ' 测试通过****************************')
                    self.resultSignal.emit(i + ' is OK')
                    break
        self.stateSignal.emit(0)

class AutoUI(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        try:
            import airtest
        except ImportError:
            self.Logbrowser.append('缺少airtest库，正在自动安装，请稍等')
            os.system('pip install airtest -i https://pypi.tuna.tsinghua.edu.cn/simple')

        self.list_add = []
        self.rootfile = ''
        self.rThread = None
        self.setWindowTitle('WP连跑小工具')

        self.resize(1051, 502)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.select = QPushButton()
        self.select.setObjectName("select")
        self.verticalLayout.addWidget(self.select)
        self.refresh = QPushButton()
        self.refresh.setObjectName("refresh")
        self.verticalLayout.addWidget(self.refresh)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.Filetree = QTreeWidget()
        self.Filetree.setObjectName("Filetree")
        self.Filetree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.Filetree.setColumnCount(1)
        self.Filetree.setHeaderLabels(['文件名'])
        self.horizontalLayout.addWidget(self.Filetree)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Run = QPushButton()
        self.Run.setObjectName("Run")
        self.verticalLayout_2.addWidget(self.Run)
        self.Resultcheck = QPushButton()
        self.Resultcheck.setObjectName("Resultcheck")
        self.verticalLayout_2.addWidget(self.Resultcheck)
        self.Clear = QPushButton()
        self.Clear.setObjectName("Clear")
        self.verticalLayout_2.addWidget(self.Clear)
        self.Savelog = QPushButton()
        self.Savelog.setObjectName("Savelog")
        self.verticalLayout_2.addWidget(self.Savelog)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.Logbrowser = QTextBrowser()
        self.Logbrowser.setMinimumSize(QSize(500, 0))
        self.Logbrowser.setObjectName("Logbrowser")
        self.horizontalLayout.addWidget(self.Logbrowser)
        self.Resultbrowser = QTextBrowser()
        self.Resultbrowser.setMinimumSize(QSize(500, 0))
        self.Resultbrowser.setObjectName("Resultbrowser")

        self.select.setText( "选择脚本目录")
        self.refresh.setText( "刷新脚本列表")
        self.Run.setText( "开始运行")
        self.Resultcheck.setText("Log/结果")
        self.Clear.setText("清空窗口")
        self.Savelog.setText("保存Log")
        self.setLayout(self.horizontalLayout)
        

        self.select.clicked.connect(self.scan_airfile)
        self.refresh.clicked.connect(self.refreshfilelist)
        self.Run.clicked.connect(self.run_airfile)
        self.Resultcheck.clicked.connect(self.logresultswap)
        self.Clear.clicked.connect(self.clearlog)
        self.Filetree.itemChanged.connect(self.checkboxStateChange)
        self.Savelog.clicked.connect(self.savelog)
        #self.Filetree.itemChanged.connect(self.onclick)



    def log_print(self,s):
        #self.Logbrowser.append(str)
        self.Logbrowser.append(s)


    def scan_airfile(self):
        self.directory = QFileDialog.getExistingDirectory(self,'选择脚本目录','')
        if str(self.directory) != self.rootfile:
            self.rootfile = str(self.directory)
            if len(str(self.directory))>0:
                self.root = QTreeWidgetItem()
                self.root.setText(0, str(self.directory))
                self.root.setCheckState(0, 0)
                dirs  = os.listdir(self.directory)
                for filespath in dirs:
                    if re.findall(r'T.*.air',filespath):
                        child = QTreeWidgetItem(self.root)
                        child.setText(0, filespath)
                        child.setCheckState(0, 0)
                self.Filetree.addTopLevelItem(self.root)
                self.Filetree.expandAll()
        else:
            self.refreshfilelist()


    def refreshfilelist(self):
        self.root.takeChildren()
        dirs  = os.listdir(self.directory)
        for filespath in dirs:
            if re.findall(r'T.*.air',filespath):
                child = QTreeWidgetItem(self.root)
                child.setText(0, filespath)
                child.setCheckState(0, 0)
        self.Filetree.addTopLevelItem(self.root)
        self.Filetree.expandAll()


    def run_airfile(self):
        if self.Run.text() == '开始运行':
            self.rThread = Runtask(rootpath = self.root)
            self.rThread.textSignal.connect(self.log_print)
            self.rThread.resultSignal.connect(self.resultcheck)
            self.rThread.stateSignal.connect(self.statecheck)
            self.rThread.start()
            self.Run.setText('停止运行')
        else:
            self.rThread.stop()
            self.Run.setText('开始运行')
            self.Logbrowser.append('\n任务已停止\n')
        #os.system('python -m airtest run ' + self.root.text(0)+ '/' + i +' --device Windows:///')


    def statecheck(self,stateSignal):
        if stateSignal == 0:
            self.Run.setText('开始运行')


    def resultcheck(self,resultSignal):
        self.Resultbrowser.append(resultSignal)


    def logresultswap(self):
        if self.Logbrowser.isVisible() == True:
            self.horizontalLayout.replaceWidget(self.Logbrowser,self.Resultbrowser)
            self.Logbrowser.hide()
            self.Resultbrowser.show()
        else:
            self.horizontalLayout.replaceWidget(self.Resultbrowser,self.Logbrowser)
            self.Resultbrowser.hide()
            self.Logbrowser.show()


    def clearlog(self):
        if self.Logbrowser.isVisible() == True:
            self.Logbrowser.clear()
        else:
            self.Resultbrowser.clear()


    def savelog(self):
        try:
            logtext = str(self.Logbrowser.toPlainText())
            with open('{}测试log.txt'.format(time.strftime('%Y-%m-%d-%H-%M', time.localtime())), 'w') as f:
                f.write(logtext)
        except Exception as e:
            print(e)


    def checkboxStateChange(self,item,column):#选中树形列表中的父节点，子节点全部选中
            count = item.childCount()
            if item.checkState(column) == Qt.Checked:
                for f in range(count):
                    item.child(f).setCheckState(0, Qt.Checked)
            if item.checkState(column) == Qt.Unchecked:
                for f in range(count):
                    item.child(f).setCheckState(0, Qt.Unchecked)
'''class redirect_stdout():
    def __init__(self):
        self.oldstdout = sys.stdout # 原控制台输出通道
    def write(self, message):
        # print('a')==sys.stdout.write('a') and sys.stdout.write('\n')
        self.oldstdout.write(message) # 仍在控制台输出
        if message!="\n": # 在PyQt的"Plain Text Edit"添加内容
            win.Logbrowser.append(message)
    def flush(self):
        pass'''



if __name__ == '__main__':
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app=QApplication(sys.argv)
    win=AutoUI()
    win.show()
    #sys.stdout = redirect_stdout()
    sys.exit(app.exec_())
