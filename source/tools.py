import cv2
import numpy as np

from algorithm import floodFill

class BaseTool:
    toolName = 'Base'
    widget = None

    def checkWidget(self):
        assert self.widget is not None, "You should call tool.setWidget before this."

    def click(self, pos):
        self.checkWidget()
        self.afterClick(pos)

    def drag(self, pos):
        self.checkWidget()
        self.afterDrag(pos)

    def release(self, pos):
        self.checkWidget()
        self.afterRelease(pos)

    def afterClick(self, pos):
        pass

    def afterDrag(self, pos):
        pass

    def afterRelease(self, pos):
        pass

    def setWidget(self, widget):
        BaseTool.widget = widget

class PainterTool(BaseTool):
    toolName = 'Painter'
    color = (128, 128, 128)

    def click(self, pos):
        self.checkWidget()
        self.widget.setHistory(self.toolName)
        self.afterClick(pos)

    def setColor(self, color):
        PainterTool.color = color

    def flush(self):
        self.checkWidget()
        self.widget.setSet()

class Pen(PainterTool):
    toolName = 'Pen'
    thickness = 5
    def __init__(self):
        self.mousePosition = None

    def afterClick(self, pos, *args):
        position = pos.x(), pos.y()
        self.mousePosition = position
        cv2.line(self.widget.trimap, position, position, self.color, 
                 thickness = self.thickness)
        self.flush()

    def afterDrag(self, pos, *args):
        position = pos.x(), pos.y()
        cv2.line(self.widget.trimap, self.mousePosition, position, 
                 self.color, thickness = self.thickness)
        self.mousePosition = position
        self.flush()

    def setThickness(self, thickness):
        Pen.thickness = thickness


class Filler(PainterTool):
    toolName = 'Filler'
    theta = 7
    def __init__(self):
        super(Filler).__init__();

    def addTheta(self, x):
        if self.theta + x >= 0:
            self.setTheta(self.theta + x)

    def setTheta(self, theta):
        if theta < 0:
            theta = 0

        Filler.theta = theta

    def getTheta(self):
        return self.theta
    
    def refill(self):
        self.widget.setHistory(self.toolName)
        self.fill(self.lasFill, self.lasColor)

    def afterClick(self, pos, *args):
        position = pos.y(), pos.x()
        self.lasFill = position
        self.lasColor = self.color
        self.fill(position, self.color)

    def fill(self, position, color):
        vis = floodFill(self.widget.grad, self.theta, position)
        vis = np.stack([vis] * 3, axis = 2)
        self.widget.trimap = (self.widget.trimap * vis + 
                             color * np.logical_not(vis)).astype('uint8')
        self.flush()

painterTools = {'Filler': Filler(), 'Pen': Pen()}

class AlphaTool(BaseTool):
    toolName = 'Alpha'

    def click(self, pos):
        self.checkWidget()
        self.widget.setAlphaHistory()
        self.afterClick(pos)

    def flush(self):
        self.checkWidget()
        self.widget.setFinal()

class Concater(AlphaTool):
    def setId(self, id):
        self.id = id

        if id > 0:
            if id - 3 < len(self.widget.outputs):
                self.clicked = self.widget.outputs[id - 3]
            else:
                self.clicked = None
        else:
            self.clicked = np.zeros(self.widget.final.shape)

        self.vis = {}
        
        return self

    def setArr(self, arrX, arrY):
        self.arrX = np.array(arrX + [0])
        self.arrY = np.array(arrY + [0])
        self.vis = {}

    def afterClick(self, pos):
        arrX = self.arrX
        arrY = self.arrY
        f = self.widget.f
        clicked = self.clicked
        if clicked is None:
            return 
        final = self.widget.final
        n, m = final.shape[:2]

        cx, cy = int(pos.y() / f), int(pos.x() / f)

        if cx < 0 or cy < 0 or cx >= n or cy >= m:
            return 

        p = (arrX <= cx).sum() - 1
        q = (arrY <= cy).sum() - 1

        if((p, q) in self.vis):
            return 

        self.vis[(p, q)] = None
        final[arrX[p - 1]: arrX[p], arrY[q - 1]: arrY[q]] = \
            clicked[arrX[p - 1]: arrX[p], arrY[q - 1]: arrY[q]]

        self.flush()

    afterDrag = afterClick
    afterRelease = afterClick
