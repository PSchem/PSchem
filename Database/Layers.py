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

    @property
    def color(self):
        return self._color

    @property
    def red(self):
        return self._color[0]

    @property
    def green(self):
        return self._color[1]

    @property
    def blue(self):
        return self._color[2]
        
    def __repr__(self):
        return "Color(" + repr(self.color) + ")"

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
        self._endStyle = self.RoundEnd #self.FlatEnd

    @property
    def style(self):
        return self._style

    @property
    def pattern(self):
        return self._pattern

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width

    @property
    def pixelWidth(self):
        return self._pixelWidth

    @pixelWidth.setter
    def pixelWidth(self, width):
        self._pixelWidth = width

    @property
    def endStyle(self):
        return self._endStyle

    @endStyle.setter
    def endStyle(self, endStyle):
        self._endStyle = endStyle

    def __repr__(self):
        return "<LinePattern " + str(self.style) + ", " + str(self.width) + ", " + str(self.pixelWidth) + ", " + repr(self.pattern) + ">"

    
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

    @property
    def style(self):
        return self._style

    @property
    def pattern(self):
        return self._pattern

    def __repr__(self):
        return "<FillPattern " + str(self.style) + ", " + repr(self.pattern) + ">"

class Layer():
    def __init__(self):
        self._name = ''
        self._type = ''
        self._zValue = 0
        self._color = Color(Color.red)
        self._linePattern = LinePattern(LinePattern.Solid, 0, 0)
        self._fillPattern = FillPattern(FillPattern.NoFill)
        self._view = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, t):
        self._type = t

    @property
    def fullName(self):
        return self.name + '/' + self.type

    @property
    def linePattern(self):
        return self._linePattern

    @linePattern.setter
    def linePattern(self, linePattern):
        self._linePattern = linePattern

    @property
    def lineWidth(self):
        return self.linePattern.width

    @lineWidth.setter
    def lineWidth(self, width):
        self.linePattern.width = width

    @property
    def linePixelWidth(self):
        return self.linePattern.pixelWidth

    @linePixelWidth.setter
    def linePixelWidth(self, width):
        self.linePattern.pixelWidth = width

    @property
    def fillPattern(self):
        return self._fillPattern

    @fillPattern.setter
    def fillPattern(self, fillPattern):
        self._fillPattern = fillPattern

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    @property
    def zValue(self):
        return self._zValue

    @zValue.setter
    def zValue(self, zValue):
        self._zValue = zValue

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, view):
        self._view = view

    @property
    def visible(self):
        return True

    @property
    def selectable(self):
        return False

    def __repr__(self):
        return "<Layer '" + self.fullName + "'@" + str(self.zValue) + ">"

class Layers():
    def __init__(self, database):
        self._database = database
        self._layers = set()
        self._layerNames = {}
        self._view = None
        self._sortedLayers = None

    @property
    def database(self):
        return self._database

    @property
    def layers(self):
        return self._layers

    @property
    def sortedLayers(self):
        """Cached list of layers sorted by zValue."""
        if not self._sortedLayers:
            self._sortedLayers = sorted(self.layers, lambda a, b: cmp(a.zValue, b.zValue))
        print self._sortedLayers
        return self._sortedLayers

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, view):
        self._view = view

    def addLayer(self, layer):
        self.layers.add(layer)
        self._layerNames[layer.fullName] = layer
        self._sortedLayers = None
        if self.view:
            self.view.addLayer(layer)

    def layerByName(self, layerName, typeName):
        fullName = layerName + '/' + typeName
        if self._layerNames.has_key(fullName):
            return self._layerNames[fullName]
        else:
            return None

    def layerNames(self):
        return self._layerNames.keys()

    def __repr__(self):
        return "<Layers " + repr(self.sortedLayers) + ">"
        
