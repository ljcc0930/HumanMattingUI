import math

from PySide2.QtWidgets import QLabel, QPushButton, QSlider

import config
import tools

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
    
class MyPushButton(QPushButton):
    def setWidget(widget):
        MyPushButton.widget = widget
        MyPushButton.buttons = {
            'Undo':             widget.undo,
            'Run':              widget.run,
            'Save':             widget.save,
            'SaveAlpha':        widget.saveAlpha,
            'Previous':         lambda : widget.newSet(True),
            'Next':             widget.newSet,
            'FillUnknown':      widget.fillUnknown,
            'UnknownUp':        widget.unknownUp,
            'UnknownDown':      widget.unknownDown,
            'Squeeze':          widget.squeeze,
            'SplitUp':          widget.splitUp,
            'SplitDown':        widget.splitDown,
            'FillerUp':         widget.fillerUp,
            'FillerDown':       lambda : widget.fillerUp(-1),
            'FillerUpTen':      lambda : widget.fillerUp(10),
            'FillerDownTen':    lambda : widget.fillerUp(-10),
            'ShowGrid':         widget.showGrid,
            'UndoAlpha':        widget.undoAlpha,
            'SolveForeground':  widget.solveForeground,
            'ChangeBG':         widget.changeBG,
        }

    def __init__(self, widget, text, command = None):
        if command is None:
            command = text

        super(MyPushButton, self).__init__(text)
        self.text = command
        # self.widget = widget
        if self.text in config.painterColors:
            self.button = lambda : self.widget.setColor(self.text)
        elif self.text in tools.painterTools:
            self.button = lambda : self.widget.setTool(self.text)
        else:
            assert self.text in self.buttons, "MyPushButton " + self.text + " not implement!"
            self.button = self.buttons[self.text]

    def mouseReleaseEvent(self, QMouseEvent):
        super(MyPushButton, self).mouseReleaseEvent(QMouseEvent)
        self.button()
        self.widget.setSet()
        self.widget.setResult()
        self.widget.setFinal()

class MySlider(QSlider):
    def __init__(self, widget, command, direction):
        super(MySlider, self).__init__(direction)
        self.command = command
        self.widget = widget
        self.commands = {
            'FillerSlider':     lambda : self.widget.setFiller(self.value()),
            'ImageAlphaSlider': lambda : self.widget.setImageAlpha(self.value()),
        }
        assert self.command in self.commands, "MySlider " + self.command + " not implement!"
        self.slider = self.commands[self.command]
        self.valueChanged.connect(self.slider)

    def setSliderType(self, minimum, maximum, type = "continuous"):
        if type == "discrete":
            self.setMinimum(minimum)
            self.setMaximum(maximum)
            self.setTickInterval((maximum - minimum) // 10)
            self.setSingleStep(1)

        f_ = 1e+5
        eps = 1 / f_
        if type == "continuous":
            minimum = int(minimum * f_)
            maximum = int(maximum * f_)
            self.setMinimum(minimum)
            self.setMaximum(maximum)
            self.setTickInterval((maximum - minimum) // 10)
            self.setSingleStep(1)
            self.value = lambda : super(MySlider, self).value() * eps
            self.setValue = lambda num: super(MySlider, self).setValue(num * f_)

        if type == "log":
            minimum = max(minimum, eps)
            minimum = int(math.log(minimum) * f_)
            maximum = int(math.log(maximum) * f_)
            self.setMinimum(minimum)
            self.setMaximum(maximum)
            self.setTickInterval((maximum - minimum) // 10)
            self.setSingleStep(1)
            self.value = lambda : math.exp(super(MySlider, self).value() * eps)
            self.setValue = lambda num: \
                super(MySlider, self).setValue(math.log(max(num, eps)) * f_)
