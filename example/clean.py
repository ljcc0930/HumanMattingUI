import sys
from PyQt4 import QtGui, QtCore


class Example(QtGui.QWidget):

  def __init__(self):
    super(Example, self).__init__()

    self.pageNumber = 1
    self.CTlist = ('ct.png', 'ct2.png', 'ct3.png')
    self.initUI(self.pageNumber)

  def initUI(self,page):

    if self.layout():
        QtGui.QWidget().setLayout(self.layout())

    lbl1 = QtGui.QLabel(self)
    button1 = QtGui.QRadioButton('Picture 1')

    lbl2 = QtGui.QLabel(self)
    button2 = QtGui.QRadioButton('Picture 2')

    button3 = QtGui.QPushButton('Next')
    button3.clicked.connect(self.next)

    pixmap = QtGui.QPixmap(self.CTlist[page])
    lbl1.setPixmap(pixmap)
    lbl2.setPixmap(pixmap)

    vbox1 = QtGui.QVBoxLayout()
    vbox1.addWidget(lbl1)
    vbox1.addWidget(button1)

    vbox2 = QtGui.QVBoxLayout()
    vbox2.addWidget(lbl2)
    vbox2.addWidget(button2)

    vbox3 = QtGui.QVBoxLayout()
    vbox3.addWidget(button3)

    hbox = QtGui.QHBoxLayout()
    hbox.addLayout(vbox1)
    hbox.addLayout(vbox2)
    hbox.addLayout(vbox3)

    self.setLayout(hbox)

    self.move(300,200)
    self.setWindowTitle('Choose which picture you like more')
    self.show()  

  def next(self):
      self.pageNumber += 1
      self.initUI(self.pageNumber)


def main():
  app = QtGui.QApplication(sys.argv)
  ex = Example()
  sys.exit(app.exec_())

if __name__== '__main__':
  main()
