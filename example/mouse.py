import sys
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QHBoxLayout)
from PySide2.QtCore import Slot, Qt, QSize
from PySide2.QtGui import QPixmap, QImage, QCursor

class Example(QWidget):        
    def __init__(self):
        super(Example, self).__init__()            
        self.initUI()
        self.keyPressed = False

    def mousePressEvent(self, QMouseEvent):
        self.keyPressed = True
        print(QMouseEvent.pos())
        cursor = QCursor()
        print(cursor.pos())

    def mouseMoveEvent(self, QMouseEvent):
        cursor = QCursor()
        print('move', cursor.pos())

    def mouseReleaseEvent(self, QMouseEvent):
        cursor = QCursor()
        print(cursor.pos())

    def initUI(self):                           
        qbtn = QPushButton('Quit', self)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 50)       

        self.setGeometry(0, 0, 1024, 768)
        self.setWindowTitle('Quit button')    
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.show()
    def test(self):
      print("test")

def main():        
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
