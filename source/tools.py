import cv2
import numpy as np

from algorithm import floodFill

class BaseTool:
    color = (128, 128, 128)
    toolName = 'Base'
    widget = None

    def checkWidget(self):
        assert self.widget is not None, "You should call tool.setWidget before this."

    def click(self, pos):
        self.checkWidget()
        self.widget.setHistory()
        self.afterClick(pos)

    def drag(self, pos):
        self.checkWidget()
        self.afterDrag(pos)

    def release(self, pos):
        self.checkWidget()
        self.afterRelease(pos)

    def flush(self):
        self.checkWidget()
        self.widget.setSet()

    def afterClick(self, pos):
        pass

    def afterDrag(self, pos):
        pass

    def afterRelease(self, pos):
        pass

    def setColor(self, color):
        BaseTool.color = color

    def setWidget(self, widget):
        BaseTool.widget = widget

class Pen(BaseTool):
    toolName = 'Pen'
    def __init__(self):
        self.mousePosition = None
        self.thickness = 5

    def afterClick(self, pos):
        position = pos.x(), pos.y()
        self.mousePosition = position
        cv2.line(self.widget.trimap, position, position, self.color, 
                 thickness = self.thickness)
        self.flush()

    def afterDrag(self, pos):
        position = pos.x(), pos.y()
        cv2.line(self.widget.trimap, self.mousePosition, position, 
                 self.color, thickness = self.thickness)
        self.mousePosition = position
        self.flush()


class Filler(BaseTool):
    toolName = 'Filler'
    theta = 7
    def __init__(self):
        super(Filler).__init__();

    def setTheta(self, theta):
        Filler.theta = theta

    def afterRelease(self, pos):
        position = pos.y(), pos.x()
        vis = floodFill(self.widget.grad, self.theta, position)
        vis = np.stack([vis] * 3, axis = 2)
        self.widget.trimap =(self.widget.trimap - self.color) * vis + self.color
        self.flush()

painterTools = {'Filler': Filler(), 'Pen': Pen()}
