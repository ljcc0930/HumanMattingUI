import sys
import json
import os
import numpy as np
import cv2

from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QHBoxLayout,
                               QSlider)
from PySide2.QtCore import Slot, Qt, QSize
from PySide2.QtGui import QPixmap, QImage, QCursor, QFont

from utils import numpytoPixmap, ImageInputs, addBlankToLayout
import tools
import config

import algorithm

from matting.deep_matting import load_model, deep_matting
from matting.closed_form_matting import closed_form_matting_with_trimap

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
    def __init__(self, widget, text, command = None):
        if command is None:
            command = text

        super(MyButton, self).__init__(text)
        self.text = command
        self.widget = widget
        self.buttons = {
            'Undo':         self.widget.undo,
            'Run':          self.widget.run,
            'Save':         self.widget.save,
            'SaveAlpha':    self.widget.saveAlpha,
            'Previous':     lambda : self.widget.newSet(True),
            'Next':         self.widget.newSet,
            'FillUnknown':  self.widget.fillUnknown,
            'UnknownUp':    self.widget.unknownUp,
            'UnknownDown':  self.widget.unknownDown,
            'Squeeze':      self.widget.squeeze,
            'SplitUp':      self.widget.splitUp,
            'SplitDown':    self.widget.splitDown,
            'FillerUp':     self.widget.fillerUp,
            'FillerDown':   lambda : self.widget.fillerUp(-1),
            'FillerUpTen':  lambda : self.widget.fillerUp(10),
            'FillerDownTen':lambda : self.widget.fillerUp(-10),
            'ShowGrid':     self.widget.showGrid,
            'UndoAlpha':    self.widget.undoAlpha,
        }
        if self.text in config.painterColors:
            self.button = lambda : self.widget.setColor(self.text)
        elif self.text in tools.painterTools:
            self.button = lambda : self.widget.setTool(self.text)
        else:
            assert self.text in self.buttons, self.text + " not implement!"
            self.button = self.buttons[self.text]

    def mouseReleaseEvent(self, QMouseEvent):
        super(MyButton, self).mouseReleaseEvent(QMouseEvent)
        self.button()
        self.widget.setSet()
        self.widget.setResult()


class MyWidget(QWidget):
    def setImage(self, x, pixmap = None, array = None, resize = False, grid = False):
        assert pixmap is None or not grid, "Pixmap cannot draw grid."

        if pixmap is None:
            if array is None:
                self.texts[x].setPixmap(None)
                return 

            array = array.astype('uint8')

            if grid:
                array = cv2.resize(array, None, fx = self.f, fy = self.f)

                for i in self.splitArrX[:-1]:
                    i = int(i * self.f)
                    array[i] = np.array((0, 255, 0))
                for i in self.splitArrY[:-1]:
                    i = int(i * self.f)
                    array[:, i] = np.array((0, 255, 0))

                resize = False

            pixmap = numpytoPixmap(array)
        imgx, imgy = self.scale
        if resize:
            pixmap = pixmap.scaled(imgx, imgy, Qt.KeepAspectRatio)
        self.texts[x].setPixmap(pixmap)

    def setFinal(self):
        if self.final is None:
            self.setImage(-1)
        else:
            alpha = self.final.mean(axis = 2) / 255.0
            show = self.changeBackground(alpha)
            self.setImage(-1, array = show, resize = True, grid = self.gridFlag)

    def setSet(self):
        self.setImage(0, array = self.image)
        self.setImage(1, array = self.trimap)
        show = self.image * 0.7 + self.trimap * 0.3
        self.setImage(2, array = show)
        self.setFinal()

    def changeBackground(self, alpha):
        image, trimap = self.resizeToNormal()
        alpha = np.stack([alpha] * 3, axis = 2)
        show = image * alpha + (1 - alpha) * np.array((0, 0, 205))
        return show

    def setResult(self):
        for i, output in enumerate(self.outputs):
            alpha = output.mean(axis = 2) / 255.0
            show = self.changeBackground(alpha)
            self.setImage(i + 3, array = show, resize = True, grid = self.gridFlag)

    def newSet(self, prev = False):
        for text in self.texts:
            text.setPixmap(None)
        if prev:
            self.image, self.trimap, self.final = self.imageList.previous()
        else:
            self.image, self.trimap, self.final = self.imageList()

        if len(self.trimap.shape) == 2:
            self.trimap = np.stack([self.trimap] * 3, axis = 2)
        assert self.image.shape == self.trimap.shape

        h, w = self.image.shape[:2]
        imgw, imgh = self.scale
        self.f = min(imgw / w, imgh / h)

        self.splitArrX = [self.image.shape[0]]
        self.splitArrY = [self.image.shape[1]]
        self.resultTool.setArr(self.splitArrX, self.splitArrY)
        for i in range(config.defaultSplit):
            self.splitUp()

        self.image = cv2.resize(self.image, None, fx = self.f, fy = self.f)
        self.trimap = cv2.resize(self.trimap, None, fx = self.f, fy = self.f)

        self.history = []
        self.alphaHistory = []
        self.outputs = []

        self.setSet()
        self.getGradient()

    def getGradient(self):
        self.grad = algorithm.calcGradient(self.image)

    def resizeToNormal(self):
        f = 1 / self.f
        image = cv2.resize(self.image, None, fx = f, fy = f)
        trimap = cv2.resize(self.trimap, None, fx = f, fy = f)
        return image, trimap

    def splitUp(self):
        def splitArr(arr):
            las = 0
            new = []
            for i in arr:
                new.append((las + i) // 2)
                new.append(i)
                las = i
            return new

        if len(self.splitArrX) < 128:
            self.splitArrX = splitArr(self.splitArrX)
            self.splitArrY = splitArr(self.splitArrY)
            self.resultTool.setArr(self.splitArrX, self.splitArrY)


    def splitDown(self):
        if len(self.splitArrX) > 2:
            self.splitArrX = self.splitArrX[1::2]
            self.splitArrY = self.splitArrY[1::2]
            self.resultTool.setArr(self.splitArrX, self.splitArrY)

    def showGrid(self):
        self.gridFlag = not self.gridFlag

    def fillerUp(self, num = 1):
        if isinstance(self.tool, tools.Filler):
            self.tool.addTheta(num)

            if self.lastCommand == "Filler":
                self.undo()
                self.tool.refill()

    def unknownUp(self):
        if self.lastCommand != "FillUnknown":
            return
        self.undo()
        self.fillWidth += 1
        self.fillUnknown(True)

    def unknownDown(self):
        if self.lastCommand != "FillUnknown":
            return

        if self.fillWidth == 1:
            return 

        self.undo()
        self.fillWidth -= 1
        self.fillUnknown(True)

    def fillUnknown(self, refill = False):
        self.setHistory("FillUnknown")
        if not refill:
            self.fillWidth = 1
        self.trimap = algorithm.fillUnknown(self.trimap, width = self.fillWidth)

    def squeeze(self):
        self.setHistory()
        self.trimap = algorithm.squeeze(self.trimap)

    def undo(self):
        self.lastCommand = None
        if len(self.history) > 0:
            self.trimap = self.history.pop()
            self.setSet()

    def undoAlpha(self):
        if len(self.alphaHistory) > 0:
            self.final = self.alphaHistory.pop()
            self.setSet()

    def save(self):
        image, trimap = self.resizeToNormal()
        self.imageList.save(trimap)

    def saveAlpha(self):
        self.imageList.saveAlpha(self.final)

    def run(self):
        image, trimap = self.resizeToNormal()
        self.outputs = []
        for i, func in enumerate(self.functions):
            output = func(image, trimap)
            if output.ndim == 2:
                output = np.stack([output] * 3, axis = 2)
            self.outputs.append(output)
        self.setResult()

    def getToolObject(self, id):
        if id in [0, 1, 2]:
            return self.tool
        if id > 2 and id < self.n or id == -1:
            return self.resultTool.setId(id)

    def click(self, pos, id):
        tool = self.getToolObject(id)
        if tool is not None:
            tool.click(pos)

    def drag(self, pos, id):
        tool = self.getToolObject(id)
        if tool is not None:
            tool.drag(pos)

    def release(self, pos, id):
        tool = self.getToolObject(id)
        if tool is not None:
            tool.release(pos)

    def setColor(self, color):
        color = config.painterColors[color]
        self.tool.setColor(color)

    def setHistory(self, command = None):
        self.lastCommand = command
        self.history.append(self.trimap.copy())

    def setAlphaHistory(self):
        self.alphaHistory.append(self.final.copy())

    def setTool(self, toolName):
        assert toolName in tools.painterTools, toolName + " not implement!!"
        self.tool = tools.painterTools[toolName]
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

        text = ClickLabel(self, -1, "")
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
        bx, by = self.buttonScale
        bC = self.buttonCol
        blankSize = self.blankSize
        self.toolWidgets = []

        for line in config.toolTexts:
            tempLine = []
            for tool in line:
                tempTool = []
                if not isinstance(tool, list):
                    tool = [tool]
                n = len(tool)
                for command in tool:
                    if command[-1] == '-':
                        pass
                    else:
                        temp = MyButton(self, config.getText(command), command)
                        temp.setFixedSize(QSize(bx, (by - config.defaultBlank * (n - 1)) // n))
                        tempTool.append(temp)
                tempLine.append(tempTool)
            self.toolWidgets.append(tempLine)

        self.toolLayout = QVBoxLayout()
        self.toolLayout.setAlignment(Qt.AlignTop)
        for line in self.toolWidgets:
            bR = (len(line) - 1) // bC + 1

            for row in range(bR):
                lineLayout = QHBoxLayout()
                lineLayout.setAlignment(Qt.AlignLeft)

                for tool in line[row * bC: (row + 1) * bC]:
                    singleToolLayout = QVBoxLayout()
                    for obj in tool:
                        singleToolLayout.addWidget(obj)
                    lineLayout.addLayout(singleToolLayout)
                self.toolLayout.addLayout(lineLayout)
                addBlankToLayout(self.toolLayout, blankSize[0])

            addBlankToLayout(self.toolLayout, blankSize[1])

    def __init__(self, imageList, functions):
        QWidget.__init__(self)

        self.functions = functions
        self.history = []

        self.imageList = imageList
        self.scale = config.imgScale
        self.n = 4 + len(functions)
        self.row = config.imgRow
        self.col = (self.n + self.row - 1) // self.row

        self.buttonScale = config.buttonScale
        self.buttonCol = config.buttonCol
        self.blankSize = config.blankSize

        self.tool = tools.painterTools['Pen']
        self.tool.setWidget(self)
        self.resultTool = tools.Concater()
        self.gridFlag = True

        self.fillWidth = 1

        self.outputs = []
        self.final = None

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
    # model1 = load_model('/home/wuxian/human_matting/models/alpha_models_0305/alpha_net_100.pth', 0)
    # model2 = load_model('/home/wuxian/human_matting/models/alpha_models_bg/alpha_net_100.pth', 0)
    '''
    model1 = load_model('/data2/human_matting/models/alpha_models_0305/alpha_net_100.pth', 0)
    model2 = load_model('/data2/human_matting/models/alpha_models_bg/alpha_net_100.pth', 0)

    a = lambda x, y : deep_matting(x, y, model1, 0)
    b = lambda x, y : deep_matting(x, y, model2, 0)
    c = lambda x, y : closed_form_matting_with_trimap(x / 255.0, y[:, :, 0] / 255.0) * 255.0
    '''
    a = lambda x, y: y
    b = lambda x, y: x
    c = lambda x, y: x / 2 + y / 2
    main('../list.txt', a, b, c)
