# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from Database.Primitives import *

class Color():
    Black   = [  0,   0,   0]
    White   = [255, 255, 255]
    Red     = [255,   0,   0]
    Green   = [  0, 255,   0]
    Blue    = [  0,   0, 255]
    
    def __init__(self, color):
        self._color = color

    def setColor(self, color):
        self._color = color

    def color(self):
        return self._color

    def lighter(self):
        a = 1.5
        return [min(255, int(self.red()*a)),
                min(255, int(self.green()*a)),
                min(255, int(self.blue()*a))]

    def darker(self):
        a = 1/1.5
        return [min(255, int(self.red()*a)),
                min(255, int(self.green()*a)),
                min(255, int(self.blue()*a))]

    def red(self):
        return self._color[0]

    def green(self):
        return self._color[1]

    def blue(self):
        return self._color[2]

class LinePattern():
    def __init__(self):
        self._solid = True

    def isSolid(self):
        return self._solid

class FillPattern():
    def __init__(self):
        self._solid = True

    def isSolid(self):
        return self._solid


class Outline(QtGui.QPen):
    def __init__(self):
        QtGui.QPen.__init(self)
        self._width = 0.15
        self._color = Color(Color.Black)
        self._pattern = LinePattern(LinePattern.Solid)
        self._pen = None

    def setWidth(self, width):
        self._width = width

    def setColor(self, color):
        self._color = color

    def setPattern(self, pattern):
        self._pattern = pattern

    def setPen(self, pen):
        self._pen = pen

    def width(self):
        return self._width

    def color(self):
        return self._color

    def pattern(self):
        return self._pattern

    def pen(self):
        return self._pen

class Fill(QtGui.QBrush):
    def __init__(self):
        QtGui.QBrush.__init__(self)
        self._color = Color(Color.Black)
        self._pattern = FillPattern(FillPattern.Solid)

    def setColor(self, color):
        self._color = color

    def setPattern(self, pattern):
        self._pattern = pattern

    def setBrush(self, brush):
        self._brush = brush

    def color(self):
        return self._color

    def pattern(self):
        return self._pattern

    def brush(self):
        return self._brush

