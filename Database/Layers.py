# -*- coding: utf-8 -*-

# Copyright (C) 2009 PSchem Contributors (see CONTRIBUTORS for details)

# This file is part of PSchem Database
 
# PSchem is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PSchem is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with PSchem Database.  If not, see <http://www.gnu.org/licenses/>.

class Color():
    Black   = [   0,    0,    0]
    White   = [0xff, 0xff, 0xff]
    Red     = [0xff,    0,    0]
    Green   = [   0, 0xff,    0]
    Blue    = [   0,    0, 0xff]
    Magenta = [0xff,    0, 0xff]
    Yellow  = [0xff, 0xff,    0]
    Cyan    = [   0, 0xff, 0xff]
    Gray    = [0xa0, 0xa0, 0xa0]

    DarkRed     = [0x80,    0,    0]
    DarkGreen   = [   0, 0x80,    0]
    DarkBlue    = [   0,    0, 0x80]
    DarkMagenta = [0x80,    0, 0x80]
    DarkYellow  = [0x80, 0x80,    0]
    DarkCyan    = [   0, 0x80, 0x80]
    DarkGray    = [0x80, 0x80, 0x80]

    LightGray    = [0xc0, 0xc0, 0xc0]

    def __init__(self, color):
        self._color = color

    def color(self):
        return self._color

    def red(self):
        return self._color[0]

    def green(self):
        return self._color[1]

    def blue(self):
        return self._color[2]

class LinePattern():
    NoLine, Solid, Dash, Dot, DashDot, DashDotDot, CustomPattern = range(7)
    FlatEnd, SquareEnd, RoundEnd = range(3)
    def __init__(self, style=Solid, width=0, pixelWidth=0, pattern=[]):
        self._style = style
        if style == self.CustomPattern:
            self._pattern = pattern
        else:
            self._pattern = []
        self._width = width
        self._pixelWidth = pixelWidth
        self._endStyle = self.FlatEnd

    def setPixelWidth(self, width):
        self._pixelWidth = width

    def setWidth(self, width):
        self._width = width

    def setEndStyle(self, endStyle):
        self._endStyle = endStyle

    def style(self):
        return self._style

    def endStyle(self):
        return self._endStyle

    def width(self):
        return self._width

    def pixelWidth(self):
        return self._pixelWidth

    def pattern(self):
        return self._pattern

class FillPattern():
    NoFill, Solid, CustomPattern, \
    Dense1, Dense2, Dense3, Dense4, Dense5, Dense6, Dense7, \
    Hor, Ver, Cross, BDiag, FDiag, DiagCross = range(16)

    def __init__(self, style=NoFill, pattern=[]):
        self._style = style
        if style == self.CustomPattern:
            self._pattern = pattern
        else:
            self._pattern = []

    def style(self):
        return self._style

    def pattern(self):
        return self._pattern


class Layer():
    def __init__(self):
        self._name = ''
        self._type = ''
        self._zValue = 0
        self._color = Color(Color.red)
        self._linePattern = LinePattern(LinePattern.Solid, 0, 0)
        self._fillPattern = FillPattern(FillPattern.NoFill)
        self._view = None

    def setName(self, name):
        self._name = name

    def setType(self, t):
        self._type = t

    def setLinePattern(self, linePattern):
        self._linePattern = linePattern

    def setLineWidth(self, width):
        self._linePattern.setWidth(width)

    def setLinePixelWidth(self, width):
        self._linePattern.setPixelWidth(width)

    def setFillPattern(self, fillPattern):
        self._fillPattern = fillPattern

    def setColor(self, color):
        self._color = color

    def setZValue(self, zValue):
        self._zValue = zValue

    def setView(self, view):
        self._view = view

    def name(self):
        return self._name

    def ltype(self):
        return self._type

    def fullName(self):
        return self._name + ' ' + self._type

    def linePattern(self):
        return self._linePattern

    def lineWidth(self):
        return self._linePattern.width()

    def linePixelWidth(self):
        return self._linePattern.pixelWidth()

    def fillPattern(self):
        return self._fillPattern

    def color(self):
        return self._color

    def zValue(self):
        return self._zValue

    def view(self):
        return self._view

    def visible(self):
        return True

    def selectable(self):
        return False

class Layers():
    def __init__(self):
        self._layers = set()
        self._layerNames = {}
        self._view = None

    def addLayer(self, layer):
        self._layers.add(layer)
        self._layerNames[layer.fullName()] = layer
        if self._view:
            self._view.addLayer(layer)

    def layerByName(self, layerName, typeName):
        fullName = layerName + ' ' + typeName
        if self._layerNames.has_key(fullName):
            return self._layerNames[fullName]
        else:
            return None

    def layers(self):
        return self._layers

    def layerNames(self):
        return keys(self._layerNames)

    def installUpdateViewHook(self, view):
        self._view = view

