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

from Database.Layers import *
from Database.Cells import *

class Element():
    def __init__(self, parent, layers):
        self._attributes = set()
        self._views = set()
        self._layers = layers
        self._parent = parent
        self._name = 'Abstract element'
        self._layer = None
        self._x = 0
        self._y = 0
        self._angle = 0
        self._hmirror = False
        self._vmirror = False
        self._visible = True
        self._editable = True

    def addAttribute(self, attrib):
        self._attributes.add(attrib)

    def installUpdateHook(self, view):
        self._views.add(view)

    def updateViews(self):
        for v in self._views:
            v.updateItem()

    def addToView(self, view):
        view.addElem()

    def removeFromView(self):
        for v in self._views:
            v.removeElem()

    def setName(self, name):
        if self._editable:
            self._name = name
            self.updateViews()

    def setLayer(self, layer):
        if self._editable:
            self._layer = layer
            self.updateViews()

    def setXY(self, x, y): #int, int
        if self._editable:
            self._x = x
            self._y = y
            self.updateViews()

    def setAngle(self, angle): #0, 90, 180, 270
        if self._editable:
            self._angle = angle
            self.updateViews()

    def setVMirror(self, mirror): #bool
        if self._editable:
            self._vmirror = mirror
            self.updateViews()

    def setHMirror(self, mirror): #bool
        if self._editable:
            self._hmirror = mirror
            self.updateViews()

    def setVisible(self, visible): #bool
        if self._editable:
            self._visible = visible
            self.updateViews()

    def attributes(self):
        return self._attributes

    def views(self):
        return self._views

    def parent(self):
        return self._parent

    def cell(self):
        return self._parent.parent()

    def library(self):
        return self.cell().parent()

    def database(self):
        return self.library().parent()

    def layers(self):
        return self._layers

    def contents(self):
        return self._attributes

    def name(self):
        return self._name

    def layer(self):
        return self._layer

    def x(self):
        return self._x

    def y(self):
        return self._y

    def angle(self):
        return self._angle

    def hMirror(self):
        return self._hmirror

    def vMirror(self):
        return self._vmirror

    def visible(self):
        return self._visible

class Attribute(Element):
    AlignLeft = 0
    AlignCenter = 1
    AlignRight = 2
    AlignBottom = 0
    AlignTop = 2
    def __init__(self, parent, layers, key, val):
        Element.__init__(self, parent, layers)
        self._key = key
        self._val = val
        self._name = 'Attr '+str(key)+' '+str(val)
        self._textSize = 1
        self._visibleKey = True
        self._hAlign = self.AlignLeft
        self._vAlign = self.AlignCenter
        self._layer = self.layers().layerByName('attribute', 'drawing')

    def setText(self, text):
        if self._editable:
            self._val = text
            self.updateViews()

    def setHAlign(self, align):
        if self._editable:
            self._hAlign = align
            self.updateViews()

    def setVAlign(self, align):
        if self._editable:
            self._vAlign = align
            self.updateViews()

    def setTextSize(self, textSize): #int in uu
        if self._editable:
            self._textSize = textSize
            self.updateViews()

    def setVisibleKey(self, visible):
        if self._editable:
            self._visibleKey = visible
            self.updateViews()

    def setHAlign(self, align):
        if self._editable:
            self._hAlign = align
            self.updateViews()

    def setVAlign(self, align):
        if self._editable:
            self._vAlign = align
            self.updateViews()

    def textSize(self):
        return self._textSize

    def visibleKey(self):
        return self._visibleKey

    def hAlign(self):
        return self._hAlign

    def vAlign(self):
        return self._vAlign

    def addToView(self, view):
        view.addAttribute(self)

    def key(self):
        return self._key

    def value(self):
        return self._val

    def text(self):
        return self._key + ': ' + self._val

class Line(Element):
    def __init__(self, parent, layers, x1, y1, x2, y2):
        Element.__init__(self, parent, layers)
        self._x = x1
        self._y = y1
        self._x2 = x2
        self._y2 = y2
        self._layer = self.layers().layerByName('annotation', 'drawing')
        self._name = 'Line '+str(x1)+' '+str(y1)+' '+str(x2)+' '+str(y2)

    def x1(self):
        return self._x

    def y1(self):
        return self._y

    def x2(self):
        return self._x2

    def y2(self):
        return self._y2

    def addToView(self, view):
        view.addLine(self)

class Pin(Element):
    def __init__(self, parent, layers, x1, y1, x2, y2):
        Element.__init__(self, parent, layers)
        self._x = x1
        self._y = y1
        self._x2 = x2
        self._y2 = y2
        self._layer = self.layers().layerByName('pin', 'drawing')
        self._name = 'Pin '+str(x1)+' '+str(y1)+' '+str(x2)+' '+str(y2)

    def x1(self):
        return self._x

    def y1(self):
        return self._y

    def x2(self):
        return self._x2

    def y2(self):
        return self._y2

    def addToView(self, view):
        view.addPin(self)

class Rect(Element):
    def __init__(self, parent, layers, x, y, w, h):
        Element.__init__(self, parent, layers)
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._name = 'Rect '+str(x)+' '+str(y)+' '+str(w)+' '+str(h)
        self._layer = self.layers().layerByName('annotation', 'drawing')

    def w(self):
        return self._w

    def h(self):
        return self._h

    def addToView(self, view):
        view.addRect(self)

class CustomPath(Element):
    move, line, curve, close = range(4)
    def __init__(self, parent, layers):
        Element.__init__(self, parent, layers)
        self._name = 'Custom path'
        self._path = []
        self._layer = self.layers().layerByName('annotation', 'drawing')

    def addToView(self, view):
        view.addCustomPath(self)

    def moveTo(self, x, y):
        if self._editable:
            self._path.append([self.move, x, y])
            self.updateViews()

    def lineTo(self, x, y):
        if self._editable:
            self._path.append([self.line, x, y])
            self.updateViews()

    def curveTo(self, xcp1, ycp1, xcp2, ycp2, x, y):
        if self._editable:
            self._path.append([self.curve, xcp1, ycp1, xcp2, ycp2, x, y])
            self.updateViews()

    def closePath(self):
        if self._editable:
            self._path.append([self.close])
            self.updateViews()

    def path(self):
        return self._path

class Ellipse(Element):
    def __init__(self, parent, layers, x, y, radiusX, radiusY):
        Element.__init__(self, parent, layers)
        self._x = x
        self._y = y
        self._radiusX = radiusX
        self._radiusY = radiusY
        self._name = 'Ellipse '+str(x)+' '+str(y)+' '+str(radiusX)+' '+str(radiusY)
        self._layer = self.layers().layerByName('annotation', 'drawing')

    def setRadius(self, radiusX, radiusY):
        if self._editable:
            self._radiusX = radiusX
            self._radiusY = radiusY
            self.updateViews()

    def radiusX(self):
        return self._radiusX

    def radiusY(self):
        return self._radiusY

    def addToView(self, view):
        view.addEllipse(self)

class EllipseArc(Element):
    def __init__(self, parent, layers, x, y, radiusX, radiusY,
                 startAngle, spanAngle):
        Element.__init__(self, parent, layers)
        self._x = x
        self._y = y
        self._radiusX = radiusX
        self._radiusY = radiusY
        self._startAngle = startAngle
        self._spanAngle = spanAngle
        self._name = 'EllipseArc '+str(x)+' '+str(y)+' '+str(radiusX)+' '+str(radiusY)
        self._layer = self.layers().layerByName('annotation', 'drawing')

    def setRadius(self, radiusX, radiusY):
        if self._editable:
            self._radiusX = radiusX
            self._radiusY = radiusY
            self.updateViews()

    def setAngles(self, startAngle, spanAngle):
        if self._editable:
            self._startAngle = startAngle
            self._spanAngle = spanAngle
            self.updateViews()

    def radiusX(self):
        return self._radiusX

    def radiusY(self):
        return self._radiusY

    def startAngle(self):
        return self._startAngle

    def spanAngle(self):
        return self._spanAngle

    def addToView(self, view):
        #pass
        view.addEllipseArc(self)

class Label(Element):
    AlignLeft = 0
    AlignCenter = 1
    AlignRight = 2
    AlignBottom = 0
    AlignTop = 2
    def __init__(self, parent, layers):
        Element.__init__(self, parent, layers)
        self._textSize = 1
        self._text = ''
        self._hAlign = self.AlignLeft
        self._vAlign = self.AlignCenter
        self._name = 'Label'
        self._layer = self.layers().layerByName('annotation', 'drawing')

    def setText(self, text):
        if self._editable:
            self._text = text
            self.updateViews()

    def setHAlign(self, align):
        if self._editable:
            self._hAlign = align
            self.updateViews()

    def setVAlign(self, align):
        if self._editable:
            self._vAlign = align
            self.updateViews()

    def setTextSize(self, textSize): #int in uu
        if self._editable:
            self._textSize = textSize
            self.updateViews()

    def textSize(self):
        return self._textSize

    def hAlign(self):
        return self._hAlign

    def vAlign(self):
        return self._vAlign

    def text(self):
        return self._text

    def addToView(self, view):
        view.addLabel(self)

class NetSegment(Element):
    def __init__(self, parent, layers, x1, y1, x2, y2):
        Element.__init__(self, parent, layers)
        self._x1 = x1
        self._x2 = x2
        self._y1 = y1
        self._y2 = y2
        self._layer = self.layers().layerByName('net', 'drawing')
        self._name = 'NetSegment '+str(x1)+' '+str(y1)+' '+str(x2)+' '+str(y2)

    def x1(self):
        return self._x1

    def y1(self):
        return self._y1

    def x2(self):
        return self._x2

    def y2(self):
        return self._y2

    def minX(self):
        return min(self._x1, self._x2)
        
    def maxX(self):
        return max(self._x1, self._x2)
        
    def minY(self):
        return min(self._y1, self._y2)
        
    def maxY(self):
        return max(self._y1, self._y2)
        
    def addToView(self, view):
        view.addNetSegment(self)
    
    def contains (self, x, y):
        c1 = (self._x1 == self._x2 and 
            self._y1 == self._y2 and
            self._x1 == x and
            self._y1 == y)
        c2 = (self._x1 == x and self._y1 == y)
        c3 = (self._x2 == x and self._y2 == y)
        return (c1 or c2 or c3)

    def containsInside (self, x, y):
        c1 = (self._x1 == self._x2 == x and 
            self.minY() < y < self.maxY())
        c2 = (self._y1 == self._y2 == y and
            self.minX() < x < self.maxX())
        #print self._x1, self._y1, self._x2, self._y2, x, y
        return (c1 or c2)

class SolderDot(Element):
    def __init__(self, parent, layers, x, y):
        Element.__init__(self, parent, layers)
        self._x = x
        self._y = y
        self._layer = self.layers().layerByName('net', 'drawing')
        self._name = 'SolderDot '+str(x)+' '+str(y)

    def addToView(self, view):
        view.addSolderDot(self)
        
    def radiusX(self):
        return self.parent().uu()
        
    def radiusY(self):
        return self.parent().uu()
        
        
class Instance(Element):
    def __init__(self, parent, layers):
        Element.__init__(self, parent, layers)
        self._libName = ''
        self._cellName = ''
        self._viewName = ''
        self._name = 'I?'

        self._cell = None
        self._cellView = None
        self._layer = self.layers().layerByName('instance', 'drawing')

    def setCell(self, libName, cellName, viewName): #string
        if self._editable:
            self._libName = libName
            self._cellName = cellName
            self._viewName = viewName
            self.updateViews()

    def instanceCell(self):
        if self._cell:    #cache
            return self._cell
        if self._libName == '':
            lib = self.library()
            self._cell = lib.cellByName(self._cellName)
        else:
            self._cell = self.database().cellByName(
                self._libName, self._cellName)
        return self._cell


    def instanceCellView(self):
        if self._cellView:   #cache
            return self._cellView
        self._cellView = self.instanceCell().viewByName('symbol')
        return self._cellView


    def addToView(self, view): #graphics view
        view.addInstance(self)




class Connectivity():
    def __init__(self):
        pass

class CNet(Connectivity):
    def __init__(self):
        pass

class CPin(Connectivity):
    def __init__(self):
        pass

class CInstancePin(Connectivity):
    def __init__(self):
        pass



