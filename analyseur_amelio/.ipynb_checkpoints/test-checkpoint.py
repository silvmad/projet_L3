from PyQt5.QtWidgets import *
from PyQt5.QtCore import (QObject, pyqtSignal, QThread)

class CountObj(QObject):
    new_int = pyqtSignal(int, name='new_int')
    
    def __init__(self):
        super(CountObj, self).__init__()
        self.i = 0
        self.c = { "cont" : True }
        #self.setText("{}".format(self.i))

    def count(self):
        while(self.c["cont"]):
            self.i += 1
            self.new_int.emit(self.i)
            #self.setText("{}".format(self.i))
        

class MainWindow(QWidget):
    start_count = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.counter = CountObj()

        self.go = QPushButton("Go")
        self.stop = QPushButton("Stop")
        self.lay = QHBoxLayout(self)
        self.lab = QLabel("0")
        
        self.lay.addWidget(self.go)
        self.lay.addWidget(self.stop)
        self.lay.addWidget(self.lab)
        self.go.clicked.connect(self.count)
        self.stop.clicked.connect(self.stop_count)
        self.counter.new_int.connect(self.new_lab)
        
        self.counter.moveToThread(self.thread)
        self.thread.start()

    def new_lab(self, i):
        self.lab.setText("{}".format(i))
        
    def count(self):
        self.counter.c["cont"] = True
        self.start_count.connect(self.counter.count)
        self.start_count.emit()
        

    def stop_count(self):
        #QMessageBox.warning(self, "Stop", "Stop")
        self.counter.c["cont"] = False
        #self.thread.quit()

if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()

    
"""
c = psycopg2.connect("host={} dbname={} user={} password={}".format("ec2-34-248-169-69.eu-west-1.compute.amazonaws.com", "d6m63hc16j3rtt", "cvezqdsakxlgtl", "7a64df5cb0b81f13c2ff82d2cf2fb46d3e1179fc1e6fd139194b0b38c70e02db"))
"""