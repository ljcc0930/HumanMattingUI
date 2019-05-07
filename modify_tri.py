import sys
import json
import os
import numpy as np
import cv2

from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QHBoxLayout)
from PySide2.QtCore import Slot, Qt, QSize
from PySide2.QtGui import QPixmap, QImage, QCursor

from utils import numpytoPixmap, ImageInputs
from tools import painterTools
from config import painterColors, toolTexts, toolKeys, colorKeys, buttonKeys

from algorithm import calcGradient


class ClickLabel(QLabel):
    def __init__(self, widget, id, text):
        super(ClickLabel, self).__init__(text)
        self.widget = widget
        self.id = id

    def mousePressEvent(self, QMouseEvent):
        self.widget.click(QMouseEvent.pos(), self.id)

    def mouseMoveEvent(self, QMouseEvent):
        self.widget.drag(QMouseEvent.pos(), self.id)

    def mouseReleaseEvent(self, QMouseEvent):
        self.widget.release(QMouseEvent.pos(), self.id)
    
class MyButton(QPushButton):
    def __init__(self, widget, text):
        super(MyButton, self).__init__(text)
        self.text = text
        self.widget = widget
        self.buttons = {
            'Undo':         self.widget.undo,
            'Run':          self.widget.run,
            'Save':         self.widget.save,
            'Previous':     lambda : self.widget.newSet(True),
            'Next':         self.widget.newSet
        }
        if self.text in painterColors:
            self.button = lambda : self.widget.setColor(self.text)
        elif self.text in painterTools:
            self.button = lambda : self.widget.setTool(self.text)
        else:
            assert self.text in self.buttons, self.text + " not implement!"
            self.button = self.buttons[self.text]

    def mouseReleaseEvent(self, QMouseEvent):
        super(MyButton, self).mouseReleaseEvent(QMouseEvent)
        self.button()


class MyWidget(QWidget):
    def setImage(self, x, pixmap = None, array = None, resize = False):
        if pixmap is None:
            pixmap = numpytoPixmap(array)
        imgx, imgy = self.scale
        if resize:
            pixmap = pixmap.scaled(imgx, imgy, Qt.KeepAspectRatio)
        self.texts[x].setPixmap(pixmap)

    def setSet(self):
        self.setImage(0, array = self.image)
        self.setImage(1, array = self.trimap)
        show = self.image * 0.7 + self.trimap * 0.3
        self.setImage(2, array = show)

    def newSet(self, prev = False):
        if prev:
            self.image, self.trimap = self.imageList.previous()
        else:
            self.image, self.trimap = self.imageList()

        if len(self.trimap.shape) == 2:
            self.trimap = np.stack([self.trimap] * 3, axis = 2)
        assert self.image.shape == self.trimap.shape

        h, w = self.image.shape[:2]
        imgw, imgh = self.scale
        self.f = min(imgw / w, imgh / h)

        self.image = cv2.resize(self.image, None, fx = self.f, fy = self.f)
        self.trimap = cv2.resize(self.trimap, None, fx = self.f, fy = self.f)
        self.history = []
        self.setSet()
        self.getGradient()

    def getGradient(self):
        self.grad = calcGradient(self.image)

    def resizeToNormal(self):
        f = 1 / self.f
        image = cv2.resize(self.image, None, fx = f, fy = f)
        trimap = cv2.resize(self.trimap, None, fx = f, fy = f)
        return image, trimap

    def undo(self):
        if len(self.history) > 0:
            self.trimap = self.history.pop()
            self.setSet()

    def save(self):
        image, trimap = self.resizeToNormal()
        self.imageList.save(trimap)

    def run(self):
        image, trimap = self.resizeToNormal()
        for i, func in enumerate(self.functions):
            output = func(image, trimap)
            self.setImage(i + 3, array = output, resize = True)

    def click(self, pos, id):
        if id < 3:
            self.tool.click(pos)
        else:
            print(id, pos.x(), pos.y())

    def drag(self, pos, id):
        if id < 3:
            self.tool.drag(pos)
        else:
            print(id, pos.x(), pos.y())

    def release(self, pos, id):
        if id < 3:
            self.tool.release(pos)
        else:
            print(id, pos.x(), pos.y())

    def setColor(self, color):
        color = painterColors[color]
        self.tool.setColor(color)

    def setHistory(self):
        self.history.append(self.trimap.copy())

    def setTool(self, toolName):
        assert toolName in painterTools, toolName + " not implement!!"
        self.tool = painterTools[toolName]
        assert self.tool.toolName == toolName, toolName + " mapping wrong object"

    def initImageLayout(self):
        n, row, col = self.n, self.row, self.col
        imgx, imgy = self.scale
        self.texts = []
        for i in range(3):
            text = ClickLabel(self, i, "None")
            text.setAlignment(Qt.AlignTop)
            text.setFixedSize(QSize(imgx, imgy))
            self.texts.append(text)

        for i, f in enumerate(self.functions):
            text = ClickLabel(self, i + 3, "")
            text.setAlignment(Qt.AlignTop)
            text.setFixedSize(QSize(imgx, imgy))
            self.texts.append(text)

        self.newSet()

        self.imageLayout = QVBoxLayout()
        for i in range(row):
            rowLayout = QHBoxLayout()
            for j in self.texts[i * col: (i + 1) * col]:
                rowLayout.addWidget(j)
            self.imageLayout.addLayout(rowLayout)

    def initToolLayout(self):
        self.toolWidgets = []

        for text in toolTexts:
            temp = MyButton(self, text)
            self.toolWidgets.append(temp)

        self.toolLayout = QVBoxLayout()
        for tool in self.toolWidgets:
            self.toolLayout.addWidget(tool)

    def __init__(self, imageList, functions):
        QWidget.__init__(self)

        self.functions = functions
        self.history = []

        self.imageList = imageList
        self.scale = (500, 400)
        self.n = 3 + len(functions)
        self.row = 2
        self.col = (self.n + self.row - 1) // self.row

        self.tool = painterTools['Pen']
        self.tool.setWidget(self)
        self.thickness = 5

        self.initImageLayout()
        self.initToolLayout()


        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.imageLayout)
        self.mainLayout.addLayout(self.toolLayout)

        self.setLayout(self.mainLayout)


def main(inputList, *args):
    inp = ImageInputs(inputList)
    app = QApplication(sys.argv)

    widget = MyWidget(imageList = inp, functions = args)
    # widget.resize(800, 600)
    widget.show()

    t = app.exec_()
    sys.exit(t)


if __name__ == "__main__":
    a = lambda x, y : y
    main('../list.txt', a)
