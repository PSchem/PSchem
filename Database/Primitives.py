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
        self._selected = False
        self._preSelected = False

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

    def setSelected(self, selected): #bool, not saved
        self._selected = selected
        self.updateViews()

    def setPreSelected(self, preSelected): #bool, not saved
        self._preSelected = preSelected
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

    def selected(self):
        return self._selected

    def preSelected(self):
        return self._preSelected

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

    def addToView(self, view):
        view.addNetSegment(self)

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


class ConcreteInstance():
    def __init__(self, cellView, instance=None, parent=None, topLevel=None):
        self._cellView = cellView
        self._instance = instance
        self._parent = parent
        self._children = None
        if topLevel:
            self._topLevel = topLevel
        else:
            self._topLevel = self

    def children(self):
        if self._children:   #cache
            return self._children
        if isinstance(self._cellView, Schematic):
            instances = self._cellView.instances()
            self._children = set()
            for i in instances:
                c = i.instanceCell()
                cv = c.implementation() #possibly schematic
                if not cv:
                    cv = c.symbol() #symbol
                self._children.add(ConcreteInstance(cv, i, self, self._topLevel))
        else:
            self._children = set()
        return self._children

    def parentInstance(self):
        return self._parent

    def instance(self):
        return self._instance

    def topLevel(self):
        return self._topLevel

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


class CellView():
    def __init__(self, name):
        self._name = name
        self._elems = set()
        self._views = set()
        self._parent = None

    def installUpdateHook(self, view):
        self._views.add(view)
        for elem in self._elems:
            elem.addToView(view)

    def addElem(self, elem):
        self._elems.add(elem)
        for view in self._views:
            elem.addToView(view)

    def removeElem(self, elem):
        elem.removeFromView()
        self._elems.remove(elem)

    def attributes(self):
        return filter(lambda e: isinstance(e, Attribute), self._elems)

    def pins(self):
        return filter(lambda e: isinstance(e, Pin), self._elems)

    def name(self):
        return self._name

    def cell(self):
        return self._cell

    def elems(self):
        return self._elems

    def setParent(self, parent):
        self._parent = parent

    def parent(self):
        return self._parent

    def remove(self):
        for e in list(self._elems):
            self.removeElem(e)
        self._parent = None
        self._views = set()

class Diagram(CellView):
    def __init__(self, name):
        CellView.__init__(self, name)
        self._lines = set()
        self._rects = set()
        self._labels = set()
        self._uu = 160 # default DB units per user units

    def setUU(self, uu):
        self._uu = uu

    def lines(self):
        return filter(lambda e: isinstance(e, Line), self.elems())

    def rects(self):
        return filter(lambda e: isinstance(e, Rect), self.elems())

    def labels(self):
        return filter(lambda e: isinstance(e, Label), self.elems())

    def uu(self):
        return self._uu


class Schematic(Diagram):
    def __init__(self, name):
        Diagram.__init__(self, name)
        self._components = set()
        self._instances = set()
        self._nets = set()

    def addNet(self, net):
        self._nets.add(net)

    def addComponent(self, component):
        self._components.add(component)

    def addInstance(self, instance):
        self._instances.add(instance)

    def components(self):
        components = map(lambda i: i.cell(), self.instances())
        return components.sort()

    def instances(self):
        return filter(lambda e: isinstance(e, Instance), self.elems())

    def nets(self):
        return filter(lambda e: isinstance(e, NetSegment), self.elems())

class Symbol(Diagram):
    def __init__(self, name):
        Diagram.__init__(self, name)

class Netlist(CellView):
    def __init__(self, name):
        CellView.__init__(self, name)


class Cell():
    def __init__(self, name):
        self._views = set()
        self._viewNames = {}
        self._name = name
        self._parent = None

    def addView(self, cellView):
        self._views.add(cellView)
        cellView.setParent(self)
        self._viewNames[cellView.name()] = cellView

    def removeView(self, cellView):
        cellView.remove()
        self._views.remove(cellView)
        del(self._viewNames[cellView.name()])

    def views(self):
        return self._views

    def viewNames(self):
        return self._viewNames.keys()

    def viewByName(self, viewName):
        if self._viewNames.has_key(viewName):
            return self._viewNames[viewName]
        else:
            return None

    def name(self):
        return self._name

    def implementation(self):
        return self.viewByName('schematic')  #currently assume it is 'schematic'

    def symbol(self):
        return self.viewByName('symbol')  #currently assume it is 'symbol'

    def setParent(self, parent):
        self._parent = parent
        
    def parent(self):
        return self._parent


class Library():
    def __init__(self, name):
        self._cells = set()
        self._cellNames = {}
        self._name = name
        self._parent = None

    def addCell(self, cell):
        self._cells.add(cell)
        cell.setParent(self)
        self._cellNames[cell.name()] = cell


    def cells(self):
        return self._cells

    def cellNames(self):
        return self._cellNames.keys()

    def cellByName(self, cellName):
        if self._cellNames.has_key(cellName):
            return self._cellNames[cellName]
        else:
            return None

    def viewByName(self, cellName, viewName):
        cell = self.cellByName(cellName)
        if cell:
            return cell.viewByName(viewName)
        else:
            return None

    def name(self):
        return self._name

    def setParent(self, parent):
        self._parent = parent
        
    def parent(self):
        return self._parent

    

class Database():
    def __init__(self):
        self._libraries = set()
        self._libraryNames = {}
        self._views = set()
        self._instanceViews = set()
        self._topLevelInstances = set()
        self._layers = None

    def installUpdateViewsHook(self, view):
        self._views.add(view)

    def installUpdateInstanceViewsHook(self, view):
        self._instanceViews.add(view)

    def updateViews(self):
        for v in self._views:
            v.update()

    def updateInstanceViews(self):
        for v in self._instanceViews:
            v.update()

    def addLibrary(self, library):
        self._libraries.add(library)
        library.setParent(self)
        self._libraryNames[library.name()] = library
        self.updateViews()

    def libraries(self):
        return self._libraries

    def libraryNames(self):
        return self._libraryNames.keys()

    def libraryByName(self, libraryName):
        if self._libraryNames.has_key(libraryName):
            return self._libraryNames[libraryName]
        else:
            return None

    def cellByName(self, libraryName, cellName):
        lib = self.libraryByName(libraryName)
        if lib:
            return lib.cellByName(cellName)
        else:
            return None

    def viewByName(self, libraryName, cellName, viewName):
        lib = self.libraryByName(libraryName)
        if lib:
            return lib.viewByName(cellName, viewName)
        else:
            return None

    def addTopLevelInstance(self, cellView):
        self._topLevelInstances.add(ConcreteInstance(cellView))
        self.updateInstanceViews()

    def removeTopLevelInstance(self, instance):
        self._topLevelInstances.remove(instance)
        self.updateInstanceViews()

    def topLevelInstances(self):
        return self._topLevelInstances

    def setLayers(self, layers):
        self._layers = layers
        self.updateViews()

    def layers(self):
        return self._layers

class Importer:
    def __init__(self, database):
        self._database = database
        self.reset()

    def reset(self):
        self._importedCellsView = set()
        self._reader = None
        self._fileList = []
        self._targetLibrary = 'work'
        self._overwrite = False
        self._recursive = True


