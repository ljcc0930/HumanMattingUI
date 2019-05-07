import cv2

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
    def __init__(self):
        super(Filler).__init__();

    #TODO
    def afterRelease(self, pos):
        raise Exception("Unimplement!!")

painterTools = {'Filler': Filler(), 'Pen': Pen()}
