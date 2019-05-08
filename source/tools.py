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
        self.widget.setHistory()
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

    def setTheta(self, theta):
        Filler.theta = theta

    def afterClick(self, pos, *args):
        position = pos.y(), pos.x()
        vis = floodFill(self.widget.grad, self.theta, position)
        vis = np.stack([vis] * 3, axis = 2)
        self.widget.trimap = (self.widget.trimap * vis + 
                             self.color * np.logical_not(vis)).astype('uint8')
        self.flush()

painterTools = {'Filler': Filler(), 'Pen': Pen()}

class Concater(BaseTool):
    def setId(self, id):
        self.id = id

        if id > 0:
            self.clicked = self.widget.outputs[id - 3]
        else:
            self.clicked = np.zeros(self.widget.final.shape)

        self.vis = {}
        
        return self

    def setK(self, k):
        self.k = k
        self.vis = {}

    def afterClick(self, pos):
        k = self.k
        f = self.widget.f
        clicked = self.clicked
        final = self.widget.final
        n, m = final.shape[:2]

        dx = (n - 1) // k + 1
        dy = (m - 1) // k + 1

        cx, cy = int(pos.y() / f), int(pos.x() / f)

        if cx < 0 or cy < 0 or cx >= n or cy >= m:
            return 

        p, q = cx // dx, cy // dy

        if((p, q) in self.vis):
            return 

        self.vis[(p, q)] = None
        final[p * dx: (p + 1) * dx, q * dy: (q + 1) * dy] = \
            clicked[p * dx: (p + 1) * dx, q * dy: (q + 1) * dy]

        self.flush()

    afterDrag = afterClick
    afterRelease = afterClick

    def flush(self):
        self.widget.setImage(-1, array = self.widget.final, resize = True)