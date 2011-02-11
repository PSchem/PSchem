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

#print 'Primitives in'

#from Layers import *
#from Cells import *
from Path import *
from Attributes import *
from xml.etree import ElementTree as et

#print 'Primitives out'

class Element():
    def __init__(self, diagram, layers):
        self._attributes = set()
        self._views = set()
        self._layers = layers
        self._diagram = diagram
        self._name = 'element'
        self._layer = None
        self._x = 0
        self._y = 0
        self._angle = 0
        self._hmirror = False
        self._vmirror = False
        self._visible = True
        self._editable = True
        diagram.elementAdded(self)

    @property
    def editable(self):
        return self._editable

    @property
    def attributes(self):
        return self._attributes

    @property
    def views(self):
        return self._views

    @property
    def diagram(self):
        return self._diagram

    @property
    def cell(self):
        return self.diagram.cell

    @property
    def library(self):
        return self.diagram.library

    @property
    def database(self):
        return self.diagram.database

    @property
    def layers(self):
        return self._layers

    @property
    def contents(self):
        return self._attributes

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if self.editable:
            self._name = name
            self.updateViews()

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, layer):
        if self.editable:
            self._layer = layer
            self.updateViews()

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x): #int
        if self.editable:
            self._x = x
            self.updateViews()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y): #int
        if self.editable:
            self._y = y
            self.updateViews()

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle): #0, 90, 180, 270
        if self.editable:
            self._angle = angle
            self.updateViews()

    @property
    def vMirror(self):
        return self._vmirror

    @vMirror.setter
    def vMirror(self, mirror): #bool
        if self.editable:
            self._vmirror = mirror
            self.updateViews()

    @property
    def hMirror(self):
        return self._hmirror

    @hMirror.setter
    def hMirror(self, mirror): #bool
        if self.editable:
            self._hmirror = mirror
            self.updateViews()

    @property
    def visible(self):
        return self._visible
        
    @visible.setter
    def visible(self, visible): #bool
        if self.editable:
            self._visible = visible
            self.updateViews()

    def addAttribute(self, attrib):
        self.attributes.add(attrib)

    def installUpdateHook(self, view):
        self.views.add(view)

    def itemAdded(self, item):
        self.views.add(item)

    def updateViews(self):
        for v in self.views:
            v.updateItem()

    def addToView(self, view):
        view.addElem()

    def removeFromView(self, view):
        view.removeElem(self)

    def removeFromViews(self):
        for v in self.views:
            v.removeElem()

    def toXml(self):
        elem = et.Element(self.name)
        elem.attrib['x'] = str(self.x)
        elem.attrib['y'] = str(self.y)
        elem.attrib['angle'] = str(self.angle)
        elem.attrib['hmirror'] = str(self.hmirror)
        elem.attrib['vmirror'] = str(self.vmirror)
        elem.attrib['visible'] = str(self.visible)
        #elem.attrib['layer'] = str(self.layer)
        return elem

    def remove(self):
        for a in self.attributes:
            a.remove()
        for v in self.views:
            v.removeItem()
        #self.diagram.elementRemoved(self)
        self.layers = None
        self.layer = None
        self.diagram = None
        
class Line(Element):
    def __init__(self, diagram, layers, x1, y1, x2, y2):
        Element.__init__(self, diagram, layers)
        self._x = x1
        self._y = y1
        self._x2 = x2
        self._y2 = y2
        self._layer = self.layers.layerByName('annotation', 'drawing')
        self._name = 'line'
        diagram.lineAdded(self)

    @property
    def x1(self):
        return self._x

    @property
    def y1(self):
        return self._y

    @property
    def x2(self):
        return self._x2

    @property
    def y2(self):
        return self._y2

    def addToView(self, view):
        view.addLine(self)

    def toXml(self):
        elem = Element.toXml(self)
        elem.attrib['x2'] = str(self.x2)
        elem.attrib['y2'] = str(self.y2)
        elem.attrib['layer'] = str(self.layer.name)
        return elem
        
class Rect(Element):
    def __init__(self, diagram, layers, x, y, w, h):
        Element.__init__(self, diagram, layers)
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._name = 'rect'
        self._layer = self.layers.layerByName('annotation', 'drawing')
        diagram.rectAdded(self)

    @property
    def w(self):
        return self._w

    @property
    def h(self):
        return self._h

    def addToView(self, view):
        view.addRect(self)

class CustomPath(Element):
    move, line, curve, close = range(4)
    def __init__(self, diagram, layers):
        Element.__init__(self, diagram, layers)
        self._name = 'custom_path'
        self._path = []
        self._layer = self.layers.layerByName('annotation', 'drawing')
        diagram.customPathAdded(self)

    @property
    def path(self):
        return self._path

    def addToView(self, view):
        view.addCustomPath(self)

    def moveTo(self, x, y):
        if self.editable:
            self._path.append([self.move, x, y])
            self.updateViews()

    def lineTo(self, x, y):
        if self.editable:
            self._path.append([self.line, x, y])
            self.updateViews()

    def curveTo(self, xcp1, ycp1, xcp2, ycp2, x, y):
        if self.editable:
            self._path.append([self.curve, xcp1, ycp1, xcp2, ycp2, x, y])
            self.updateViews()

    def closePath(self):
        if self.editable:
            self._path.append([self.close])
            self.updateViews()

class Ellipse(Element):
    def __init__(self, diagram, layers, x, y, radiusX, radiusY):
        Element.__init__(self, diagram, layers)
        self._x = x
        self._y = y
        self._radiusX = radiusX
        self._radiusY = radiusY
        self._name = 'ellipse'
        self._layer = self.layers.layerByName('annotation', 'drawing')
        diagram.ellipseAdded(self)

    @property
    def radiusX(self):
        return self._radiusX

    @radiusX.setter
    def radiusX(self, radiusX):
        if self.editable:
            self._radiusX = radiusX
            self.updateViews()

    @property
    def radiusY(self):
        return self._radiusY

    @radiusX.setter
    def radiusY(self, radiusY):
        if self.editable:
            self._radiusY = radiusY
            self.updateViews()

    def addToView(self, view):
        view.addEllipse(self)

class EllipseArc(Element):
    def __init__(self, diagram, layers, x, y, radiusX, radiusY,
                 startAngle, spanAngle):
        Element.__init__(self, diagram, layers)
        self._x = x
        self._y = y
        self._radiusX = radiusX
        self._radiusY = radiusY
        self._startAngle = startAngle
        self._spanAngle = spanAngle
        self._name = 'ellipse_arc '
        self._layer = self.layers.layerByName('annotation', 'drawing')
        diagram.ellipseArcAdded(self)

    @property
    def radiusX(self):
        return self._radiusX

    @radiusX.setter
    def radiusX(self, radiusX):
        if self.editable:
            self._radiusX = radiusX
            self.updateViews()

    @property
    def radiusY(self):
        return self._radiusY

    @radiusY.setter
    def radiusY(self, radiusY):
        if self.editable:
            self._radiusY = radiusY
            self.updateViews()

    @property
    def startAngle(self):
        return self._startAngle

    @startAngle.setter
    def startAngle(self, startAngle):
        if self.editable:
            self._startAngle = startAngle
            self.updateViews()

    @property
    def spanAngle(self):
        return self._spanAngle
    
    @spanAngle.setter
    def spanAngle(self, spanAngle):
        if self.editable:
            self._spanAngle = spanAngle
            self.updateViews()

    def addToView(self, view):
        view.addEllipseArc(self)

class Label(Element):
    AlignLeft = 0
    AlignCenter = 1
    AlignRight = 2
    AlignBottom = 0
    AlignTop = 2
    def __init__(self, diagram, layers):
        Element.__init__(self, diagram, layers)
        self._textSize = 1
        self._text = ''
        self._hAlign = self.AlignLeft
        self._vAlign = self.AlignCenter
        self._name = 'label'
        self._layer = self.layers.layerByName('annotation', 'drawing')
        diagram.labelAdded(self)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if self.editable:
            self._text = text
            self.updateViews()

    @property
    def textSize(self):
        return self._textSize

    @textSize.setter
    def textSize(self, textSize): #int in uu
        if self.editable:
            self._textSize = textSize
            self.updateViews()

    @property
    def hAlign(self):
        return self._hAlign

    @hAlign.setter
    def hAlign(self, align):
        if self.editable:
            self._hAlign = align
            self.updateViews()

    @property
    def vAlign(self):
        return self._vAlign

    @vAlign.setter
    def vAlign(self, align):
        if self.editable:
            self._vAlign = align
            self.updateViews()

    def addToView(self, view):
        view.addLabel(self)

    def toXml(self):
        elem = Element.toXml(self)
        elem.text = str(self.text)
        elem.attrib['halign'] = str(self.hAlign)
        elem.attrib['valign'] = str(self.vAlign)
        elem.attrib['size'] = str(self.textSize)
        return elem
        
class AttributeLabel(Label):
    AlignLeft = 0
    AlignCenter = 1
    AlignRight = 2
    AlignBottom = 0
    AlignTop = 2
    def __init__(self, diagram, layers, key, val):
        Element.__init__(self, diagram, layers)
        self._textSize = 1
        self._text = ''
        self._hAlign = self.AlignLeft
        self._vAlign = self.AlignCenter

        self._attribute = Attribute(key, val, Attribute.AInteger, self)
        self._name = 'attributeLabel'
        self._visibleKey = True
        self._layer = self.layers.layerByName('attribute', 'drawing')
        diagram.attributeLabelAdded(self)

    @property
    def attribute(self):
        return self._attribute

    @property
    def key(self):
        return self.attribute.name

    @property
    def value(self):
        return self.attribute.val

    @property
    def text(self):
        return self.key + ': ' + self.value

    @text.setter
    def text(self, text):
        if self.editable:
            self.attribute.val = text
            self.updateViews()

    @property
    def visibleKey(self):
        return self._visibleKey

    @visibleKey.setter
    def visibleKey(self, visible):
        if self.editable:
            self._visibleKey = visible
            self.updateViews()

    def addToView(self, view):
        view.addAttributeLabel(self)

    def toXml(self):
        elem = Label.toXml(self)
        elem.attrib['visibleKey'] = str(self.visibleKey)
        attr = et.Element('attribute')
        attr.attrib['name'] = self.attribute.name
        attr.attrib['type'] = self.attribute.type
        attr.text = self.attribute.val
        elem.append(attr)
        return elem
        
        
class NetSegment(Element):
    def __init__(self, diagram, layers, x1, y1, x2, y2):
        Element.__init__(self, diagram, layers)
        self._x = x1
        self._x2 = x2
        self._y = y1
        self._y2 = y2
        self._layer = self.layers.layerByName('net', 'drawing')
        self._name = 'net_segment'
        diagram.netSegmentAdded(self)

    @property
    def x1(self):
        return self._x

    @property
    def y1(self):
        return self._y

    @property
    def x2(self):
        return self._x2

    @property
    def y2(self):
        return self._y2

    @property
    def minX(self):
        return min(self.x1, self.x2)
        
    @property
    def maxX(self):
        return max(self.x1, self.x2)
        
    @property
    def minY(self):
        return min(self.y1, self.y2)
        
    @property
    def maxY(self):
        return max(self.y1, self.y2)
        
    @property
    def dx(self):
        return self.x2 - self.x1
        
    @property
    def dy(self):
        return self.y2 - self.y1
        
    @property
    def isHorizontal(self):
        return self.y1 == self.y2
        
    @property
    def isVertical(self):
        return self.x1 == self.x2
        
    @property
    def isDiagonal45(self):
        return self.dx == self.dy
        
    @property
    def isDiagonal135(self):
        return self.dx == self.dy
        
    def addToView(self, view):
        view.addNetSegment(self)
        
    def removeFromView(self, view):
        "remove from view ", view
        view.removeNetSegment(self)
        
    def splitAt(self, point):
        diagram = self.diagram
        layers = self.layers
        x1 = self.x1
        y1 = self.y1
        x2 = self.x2
        y2 = self.y2
        #first remove, then add, or a recursive loop will be triggered
        #when newly created net will call splitAt again at same point
        self.remove()
        ns1 = NetSegment(diagram, layers, x1, y1, point[0], point[1])
        ns2 = NetSegment(diagram, layers, point[0], point[1], x2, y2)
    
    def mergeSegments(self, segments):
        "Merges a list of overlying segments"
        diagram = self.diagram
        layers = self.layers
        minX = self.minX
        minY = self.minY
        maxX = self.maxX
        maxY = self.maxY
        for s in segments:
            minX = min(minX, s.minX)
            minY = min(minY, s.minY)
            maxX = max(maxX, s.maxX)
            maxY = max(maxY, s.maxY)
        #print self.__class__.__name__, minX, minY, maxX, maxY
        for s in segments:
            s.remove()
        ns = NetSegment(diagram, layers, minX, minY, maxX, maxY)

    def remove(self):
        #self._layer = None
        self.diagram.netSegmentRemoved(self)
        Element.remove(self)
 
class SolderDot(Element):
    def __init__(self, diagram, layers, x, y):
        Element.__init__(self, diagram, layers)
        self._x = x
        self._y = y
        self._layer = self.layers.layerByName('net', 'drawing')
        self._name = 'solder_dot'
        diagram.solderDotAdded(self)

    @property
    def radiusX(self):
        return self.diagram.uu
        
    @property
    def radiusY(self):
        return self.diagram.uu
        
    def addToView(self, view):
        view.addSolderDot(self)
        
class Instance(Element):
    def __init__(self, diagram, layers):
        Element.__init__(self, diagram, layers)
        self._instanceLibPath = ''
        self._instanceCellName = ''
        self._instanceCellViewName = ''
        self._name = 'instance'

        self._instanceLibrary = None
        self._instanceCell = None
        self._instanceCellView = None
        self._requestedInstanceCellView = None
        self._layer = self.layers.layerByName('instance', 'drawing')
        diagram.instanceAdded(self)

    @property
    def instanceCell(self):
        if self._instanceCell:    #cache
            return self._instanceCell
        cv = self.requestedInstanceCellView
        if cv:
            self._instanceCell = cv.cell
        else:
            path = Path.createFromNames('sym.analog', 'voltage-1')
            self._instanceCell = self.database.libraries.objectByPath(path)
        return self._instanceCell

    @property
    def instanceCellView(self):
        if self._instanceCellView:   #cache
            return self._instanceCellView
        cv = self.requestedInstanceCellView
        if cv:
            self._instanceCellView = cv
        else:
            path = Path.createFromNames('sym.analog', 'voltage-1', 'symbol')
            self._instanceCellView = self.database.libraries.objectByPath(path)
        return self._instanceCellView

    @property
    def instanceLibraryPath(self):
        return self._instanceLibPath
        
    @instanceLibraryPath.setter
    def instanceLibraryPath(self, path):
        if self.editable:
            self._instanceLibPath = path
            self.updateViews()
        
    @property
    def instanceAbsolutePath(self):
        path = self.instanceLibraryPath
        #path = Library.concatenateLibraryPaths(self.library.path, self.instanceLibraryPath)
        return path

    @property
    def instanceCellName(self):
        return self._instanceCellName
        
    @instanceCellName.setter
    def instanceCellName(self, name):
        if self.editable:
            self._instanceCellName = name
        
    @property
    def instanceCellViewName(self):
        return self._instanceCellViewName
        
    @instanceCellViewName.setter
    def instanceCellViewName(self, name):
        if self.editable:
            self._instanceViewCellName = name
            self.updateViews()
        
    @property
    def requestedInstanceCellView(self):
        if self.instanceLibraryPath == '':
            path = Path.createFromNames('.', self.instanceCellName, self.instanceCellViewName)
            self._requestedInstanceCellView = self.library.objectByPath(path)
            #self._requestedInstanceCellView = self.library.cellViewByName(self.instanceCellName, self.instanceCellViewName)
        else:
            path = Path.createFromNames(self.instanceAbsolutePath, self.instanceCellName, self.instanceCellViewName)
            self._requestedInstanceCellView = self.database.libraries.objectByPath(path)
            #self._requestedInstanceCellView = self.database.cellViewByName(self.instanceAbsolutePath, self.instanceCellName, self.instanceCellViewName)
        return self._requestedInstanceCellView
        
    @property
    def instanceLibrary(self):
        if self._instanceLibrary:    #cache
            return self._instanceLibrary
        cv = self.requestedInstanceCellView
        if cv:
            self._instanceLibrary = cv.library
        else:
            self._instanceLibrary = self.database.libraryByPath(Path.createFromPathName('sym.analog'))
        return self._instanceLibrary

    def addToView(self, view):
        view.addInstance(self)

class Pin(Instance):
    def __init__(self, diagram, layers, x1, y1, x2, y2):
        Element.__init__(self, diagram, layers)
        self._x = x1
        self._y = y1
        self._x2 = x2
        self._y2 = y2
        self._layer = self.layers.layerByName('pin', 'drawing')
        self._name = 'pin'

        self._instanceLibPath = ''
        self._instanceCellName = ''
        self._instanceCellViewName = ''
        self._name = 'instance'

        self._instanceLibrary = None
        self._instanceCell = None
        self._instanceCellView = None
        self._requestedInstanceCellView = None
        diagram.pinAdded(self)
        
    @property
    def x1(self):
        return self._x

    @property
    def y1(self):
        return self._y

    @property
    def x2(self):
        return self._x2

    @property
    def y2(self):
        return self._y2

    def addToView(self, view):
        view.addPin(self)

class SymbolPin(Instance):
    def __init__(self, diagram, layers, x1, y1, x2, y2):
        Element.__init__(self, diagram, layers)
        self._x = x1
        self._y = y1
        self._x2 = x2
        self._y2 = y2
        self._layer = self.layers.layerByName('pin', 'drawing')
        self._name = 'pin'

        self._instanceLibPath = ''
        self._instanceCellName = ''
        self._instanceCellViewName = ''
        self._name = 'instance'

        self._instanceLibrary = None
        self._instanceCell = None
        self._instanceCellView = None
        self._requestedInstanceCellView = None
        diagram.symbolPinAdded(self)
        
    @property
    def x1(self):
        return self._x

    @property
    def y1(self):
        return self._y

    @property
    def x2(self):
        return self._x2

    @property
    def y2(self):
        return self._y2

    def addToView(self, view):
        view.addPin(self)
        
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
