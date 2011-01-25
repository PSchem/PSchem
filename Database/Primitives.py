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
#from Database.Cells import *
from Database.Attributes import *
from xml.etree import ElementTree as et

class Element():
    def __init__(self, parent, layers):
        self._attributes = set()
        self._views = set()
        self._layers = layers
        self._parent = parent
        self._name = 'element'
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
        return self._parent.cell()

    def library(self):
        return self._parent.library()

    def database(self):
        return self._parent.database()

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
        
    def toXml(self):
        elem = et.Element(self._name)
        elem.attrib['x'] = str(self._x)
        elem.attrib['y'] = str(self._y)
        elem.attrib['angle'] = str(self._angle)
        elem.attrib['hmirror'] = str(self._hmirror)
        elem.attrib['vmirror'] = str(self._vmirror)
        elem.attrib['visible'] = str(self._visible)
        #elem.attrib['layer'] = str(self._layer)
        return elem

        
class Line(Element):
    def __init__(self, parent, layers, x1, y1, x2, y2):
        Element.__init__(self, parent, layers)
        self._x = x1
        self._y = y1
        self._x2 = x2
        self._y2 = y2
        self._layer = self.layers().layerByName('annotation', 'drawing')
        self._name = 'line'

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

    def toXml(self):
        elem = Element.toXml(self)
        elem.attrib['x2'] = str(self._x2)
        elem.attrib['y2'] = str(self._y2)
        elem.attrib['layer'] = str(self._layer.name())
        return elem
        
        
class Pin(Element):
    def __init__(self, parent, layers, x1, y1, x2, y2):
        Element.__init__(self, parent, layers)
        self._x = x1
        self._y = y1
        self._x2 = x2
        self._y2 = y2
        self._layer = self.layers().layerByName('pin', 'drawing')
        self._name = 'pin'

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
        self._name = 'rect'
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
        self._name = 'custom_path'
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
        self._name = 'ellipse'
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
        self._name = 'ellipse_arc '
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
        self._name = 'label'
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

    def toXml(self):
        elem = Element.toXml(self)
        elem.text = str(self._text)
        elem.attrib['halign'] = str(self._hAlign)
        elem.attrib['valign'] = str(self._vAlign)
        elem.attrib['size'] = str(self._textSize)
        return elem
        
class AttributeLabel(Label):
    AlignLeft = 0
    AlignCenter = 1
    AlignRight = 2
    AlignBottom = 0
    AlignTop = 2
    def __init__(self, parent, layers, key, val):
        Label.__init__(self, parent, layers)
        self._attribute = Attribute(key, val, Attribute.AInteger, self)
        self._name = 'attributeLabel'
        self._visibleKey = True
        self._layer = self.layers().layerByName('attribute', 'drawing')

    def setText(self, text):
        if self._editable:
            self._attribute.setVal(text)
            self.updateViews()

    def setVisibleKey(self, visible):
        if self._editable:
            self._visibleKey = visible
            self.updateViews()

    def visibleKey(self):
        return self._visibleKey

    def addToView(self, view):
        view.addAttribute(self)

    def key(self):
        return self._attribute.name()

    def value(self):
        return self._attribute.val()

    def text(self):
        return self.key() + ': ' + self.value()

    def toXml(self):
        elem = Label.toXml(self)
        elem.attrib['visibleKey'] = str(self._visibleKey)
        attr = et.Element('attribute')
        attr.attrib['name'] = self._attribute.name()
        attr.attrib['type'] = self._attribute.type()
        attr.text = self._attribute.val()
        elem.append(attr)
        return elem
        
        
class NetSegment(Element):
    def __init__(self, parent, layers, x1, y1, x2, y2):
        Element.__init__(self, parent, layers)
        self._x = x1
        self._x2 = x2
        self._y = y1
        self._y2 = y2
        self._layer = self.layers().layerByName('net', 'drawing')
        self._name = 'net_segment'

    def x1(self):
        return self._x

    def y1(self):
        return self._y

    def x2(self):
        return self._x2

    def y2(self):
        return self._y2

    def minX(self):
        return min(self._x, self._x2)
        
    def maxX(self):
        return max(self._x, self._x2)
        
    def minY(self):
        return min(self._y, self._y2)
        
    def maxY(self):
        return max(self._y, self._y2)
        
    def addToView(self, view):
        view.addNetSegment(self)
    
    def contains (self, x, y):
        c1 = (self._x == self._x2 and 
            self._y == self._y2 and
            self._x == x and
            self._y == y)
        c2 = (self._x == x and self._y == y)
        c3 = (self._x2 == x and self._y2 == y)
        return (c1 or c2 or c3)

    def containsInside (self, x, y):
        c1 = (self._x == self._x2 == x and 
            self.minY() < y < self.maxY())
        c2 = (self._y == self._y2 == y and
            self.minX() < x < self.maxX())
        #print self._x, self._y, self._x2, self._y2, x, y
        return (c1 or c2)

class SolderDot(Element):
    def __init__(self, parent, layers, x, y):
        Element.__init__(self, parent, layers)
        self._x = x
        self._y = y
        self._layer = self.layers().layerByName('net', 'drawing')
        self._name = 'solder_dot'

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
        self._name = 'instance'

        self._cell = None
        self._cellView = None
        self._layer = self.layers().layerByName('instance', 'drawing')

    def setCell(self, libName, cellName, viewName): #string
        if self._editable:
            self._libName = libName
            self._cellName = cellName
            self._viewName = viewName
            self.updateViews()

    def cell(self):
        if self._cell:    #cache
            return self._cell
        if self._libName == '':
            lib = self.library()
            self._cell = lib.cellByName(self._cellName)
        else:
            self._cell = self.database().cellByName(
                self._libName, self._cellName)
        if not self._cell:
            self._cell = self.database().cellByName('analog', 'voltage-1')
        return self._cell


    def cellView(self):
        if self._cellView:   #cache
            return self._cellView
        #print self._cellName
        cell = self.cell()
        if cell and cell.viewByName('symbol'):
            self._cellView = cell.viewByName('symbol')
        else:
            self._cellView = self.database().viewByName('analog', 'voltage-1', 'symbol')
        return self._cellView


    def addToView(self, view): #graphics view
        view.addInstance(self)

class Occurrence():
    def __init__(self, cellView, instance=None, parentOccurrence=None):
        self._cellView = cellView
        self._instance = instance
        self._parentOccurrence = parentOccurrence
        self._childOccurrences = None
        if self._parentOccurrence:
            self._topLevelOccurrence = self._parentOccurrence.topLevelOccurrence()
        else:
            self._topLevelOccurrence = self
 
    def childOccurrences(self):
        if self._childOccurrences:   #cache
            return self._childOccurrences
        #if isinstance(self._cellView, Database.Cells.Schematic):
        if self._cellView.name() == "schematic":
            instances = self._cellView.instances()
            self._childOccurrences = set()
            for i in instances:
                c = i.cell()
                #print c
                #cv = None
                cv = c.implementation() #possibly schematic
                if not cv:
                    cv = c.symbol() #symbol
                self._childOccurrences.add(Occurrence(cv, i, self))
        else:
            self._childOccurrences = set()
        return self._childOccurrences

    def parentOccurrence(self):
        return self._parentOccurrence

    def instance(self):
        return self._instance

    def topLevelOccurrence(self):
        return self._topLevelOccurrence

    def cellView(self):
        return self._cellView



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
