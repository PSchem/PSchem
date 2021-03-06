# -*- coding: utf-8 -*-

# Copyright (C) 2009 PSchem Contributors (see CONTRIBUTORS for details)

# This file is part of PSchem.
 
# PSchem is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PSchem is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with PSchem.  If not, see <http://www.gnu.org/licenses/>.

import Globals
Qt = __import__(Globals.UI,  globals(),  locals(),  ['QtCore',  'QtGui'])
QtCore = Qt.QtCore
QtGui = Qt.QtGui

#from PyQt4 import QtCore, QtGui
from Database.Primitives import *

class BaseItem(QtGui.QGraphicsItem):
    def __init__(self, parent=None):
        QtGui.QGraphicsItem.__init__(self, parent)
        
        self._boundingRect = QtCore.QRectF()
        self.model = None
        self.selected = False
        self.preSelected = False
        
    #@property
    #def model(self):
    #    return self._model

    #@model.setter
    #def setModel(self, model):
    #    self._model = model
        
    #@property
    #def selected(self):
    #    return self._selected

    #@selected.setter
    #def setSelected(self, sel):
    #    self._selected = sel
        
    #@property
    #def preSelected(self):
    #    return self._preSelected
        
    #@preSelected.setter
    #def setPreSelected(self, sel):
    #    self._preSelected = sel

    #has to be a function for QGraphicsItem compat.
    def boundingRect(self):
        return self._boundingRect
    
    def removeItem(self):
        if self.scene():
            #print "   scene? ", self
            self.scene().removeItem(self)
        else:
            print "no scene? ", self

    def updateBoundingRect(self):
        return QtCore.QRectF()
        
class TextItemInt(QtGui.QGraphicsSimpleTextItem):
    def __init__(self, parent):
        QtGui.QGraphicsSimpleTextItem.__init__(self, parent)
        self._metrics = QtGui.QFontMetricsF(self.font())
        self.draw = True
        #self.setCacheMode(QtGui.QGraphicsItem.ItemCoordinateCache) #, QtCore.QSize(128, 32) )
        #self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)

    def paint(self, painter, option, widget):
        #if (option.levelOfDetail * self._metrics.height() > 10):
        #if (option.levelOfDetail > 0.32):
        if self.draw:
            #painter.setRenderHint(QtGui.QPainter.TextAntialiasing, False)
            QtGui.QGraphicsSimpleTextItem.paint(
                self, painter, option, widget)
        #if self.parentItem().selected():
        #    pen = QtGui.QPen(self.parentItem().model.layers().layerByName('selection', 'drawing').view().pen())
        #    painter.setPen(pen)
        #    painter.drawRect(self.boundingRect())

    def updateMatrix(self):
        #self.prepareGeometryChange()
        sm = self.transform()
        s11 = sm.m11()
        s12 = sm.m12()
        s21 = sm.m21()
        s22 = sm.m22()
        sdx = sm.dx()
        sdy = sm.dy()
        
        m = self.sceneTransform()
        m11 = m.m11()
        m12 = m.m12()
        m21 = m.m21()
        m22 = m.m22()
        mdx = m.dx()
        mdy = m.dy()

        #print m11, m12, m21, m22, s11, s12, s21, s22
        self._metrics = QtGui.QFontMetricsF(self.font())
        ascent = self._metrics.ascent()
        descent = self._metrics.descent()
        h = ascent - descent
        w = self.boundingRect().width()

        label = self.parentItem().model
        if (label.vAlign == Label.AlignTop):
            vOffs = descent
        elif (label.vAlign == Label.AlignBottom):
            vOffs = ascent
        else:
            vOffs = (ascent + descent) / 2.0

        if (label.hAlign == Label.AlignLeft):
            hOffs = 0
        elif (label.hAlign == Label.AlignRight):
            hOffs = -w
        else:
            hOffs = -w / 2.0


        dx = 0
        dy = 0
        if m11 < 0 or m12 < 0:
            dx = w
        if m21 < 0 or m22 > 0:
            dy = h

        transform = QtGui.QTransform(
            s11*(cmp(m11, 0)+cmp(m12, 0)), 0,
            0, s22*(-cmp(m22,0)+cmp(m21, 0)),
            hOffs+dx, vOffs+dy)
        #self.prepareGeometryChange()
        #self.parentItem().prepareGeometryChange()
        self.setTransform(transform)
        #self.prepareGeometryChange()
        
    #def boundingRect(self):
        #return QtCore.QRectF(self._metrics.boundingRect(
        #    QtCore.QRectF(), None, self.text()))
        #    return self.rect

class TextItem(BaseItem):
    def __init__(self, label, parent=None):
        BaseItem.__init__(self, parent)
        self.model = label
        self.labelItem = TextItemInt(self)
        self.scale = 1.0
        self._boundingRect = None
        
        #self._labelItem
        self.setHandlesChildEvents(True)
        
        #self.addToGroup(self._labelItem)
        
        self.updateItem()
        self.updateMatrix()
        self.model.installUpdateHook(self)

    def updateItem(self):
        #self._labelItem.prepareGeometryChange()
        uu = float(self.model.diagram.uu)
        text = self.model.text
        #text = ''
        self.labelItem.setText(text)
        textSize = self.model.textSize
        angle = self.model.angle
        x = self.model.x/uu
        y = self.model.y/uu
        self.setVisible(self.model.visible)
        hMirror = self.model.hMirror
        vMirror = self.model.vMirror
        #self._font = QtGui.QFont(self.model.font(), 10, QtGui.QFont.Normal, False)
        font = QtGui.QFont('Helvetica', 12, 0, False)
        #font = QtGui.QFont('Helvetica', 72, QtGui.QFont.Light, False)
        #font.setStyleStrategy(QtGui.QFont.NoAntialias)

        self.labelItem.setFont(font)
        metrics = QtGui.QFontMetricsF(font)
        ascent = metrics.ascent()
        descent = metrics.descent()

        scale = textSize/(ascent-descent)/uu

        matrix = QtGui.QTransform(
            scale, 0, 0, scale, x, y)
        #matrixItem = QtGui.QTransform(
        #    1, 0, 0, -1, 0, ascent)
        #matrixItem.rotate(angle)
        brush = QtGui.QBrush(self.model.layer.view.fontBrush)
        self.labelItem.setBrush(brush)
        #self.labelItem.prepareGeometryChange()
        #self.labelItem.setTransform(matrixItem)
        self.setTransform(matrix)
        #print self.model, self.model.layer, self.model.layer.zValue
       
        self.setZValue(self.model.layer.zValue)
        self.updateBoundingRect()
        self.update(self.boundingRect())

    def updateMatrix(self):
        #return
        #self.prepareGeometryChange()
        self.labelItem.updateMatrix()
        self.updateBoundingRect()
        
    def updateBoundingRect(self):
        self.prepareGeometryChange()
        r = self.labelItem.boundingRect()
        pos = self.labelItem.pos()
        matrix = self.labelItem.transform() * QtGui.QTransform().translate(pos.x(), pos.y())
        self._boundingRect = matrix.mapRect(r)
    
    def paint(self, painter, option, widget):
        #draw = (option.levelOfDetail > 0.32)
        #if QtCore.QT_VERSION >= 263680: #4.6.0
        if Globals.QtVersion[1] >= 6:
            draw = (option.levelOfDetailFromTransform(painter.transform()) > 0.32)
        else:
            draw = (option.levelOfDetail > 0.32)
        self.labelItem.draw = draw
           
        #painter.drawLine(-2, 0, 2, 0)
        #painter.drawLine(0, -2, 0, 2)
        if not self.parentItem() and self.selected:
            pen = QtGui.QPen(self.model.layers.layerByName('selection', 'drawing').view.pen)
            painter.setPen(pen)
            #painter.drawRect(self._labelItem.boundingRect())
            painter.drawRect(self.boundingRect())

class CustomPathItem(BaseItem):
    def __init__(self, path, parent=None):
        BaseItem.__init__(self, parent)
        self.model = path
        self.path = QtGui.QPainterPath()

        #self.aa = True
        self.aa = False

        self.updateItem()
        self.model.installUpdateHook(self)

    def paint(self, painter, option, widget):
        #scale = painter.deviceMatrix().m11()
        transform = painter.transform()
        scale = abs(transform.m11())+abs(transform.m12())
        #scale = abs(option.matrix.m11())+abs(option.matrix.m12())
        #print scale
        layer = self.model.layer
        pen = QtGui.QPen(layer.view.pen)
        if not self.parentItem() and self.selected:
            pen.setColor(self.model.layers.layerByName('selection', 'drawing').view.color)
        width = layer.lineWidth
        pixelWidth = layer.linePixelWidth
        if width > 0:
            if self.aa:
                pen.setWidthF(max(pixelWidth/scale, width))
            else:
                pen.setWidth(max(scale*width, pixelWidth))

        painter.setPen(pen)
        brush = QtGui.QBrush(self.model.layer.view.brush)
        brush.setMatrix(painter.worldMatrix().inverted()[0])
        painter.setBrush(brush)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, self.aa)
        painter.drawPath(self.path)

    def updateItem(self):
        uu = float(self.model.diagram.uu)
        self.path = QtGui.QPainterPath()
        for e in self.model.path:
            if e[0] == CustomPath.move:
                self.path.moveTo(e[1]/uu, e[2]/uu)
            elif e[0] == CustomPath.line:
                self.path.lineTo(e[1]/uu, e[2]/uu)
            elif e[0] == CustomPath.curve:
                self.path.cubicTo(e[1]/uu, e[2]/uu,
                          e[3]/uu, e[4]/uu,
                          e[5]/uu, e[6]/uu)
            elif e[0] == CustomPath.close:
                self.path.closeSubpath()
        #self.width = self.model.width()
        self.setZValue(self.model.layer.zValue)
        #self.prepareGeometryChange()
        #self.setPath(p)
        self.updateBoundingRect()
        

    def updateBoundingRect(self):
        self.prepareGeometryChange()
        self._boundingRect = self.path.controlPointRect()
        a = self.model.layer.lineWidth/2.0
        self._boundingRect.adjust(-a,-a,a,a)
        
class LineItem(BaseItem):
    def __init__(self, line, parent=None):
        BaseItem.__init__(self, parent)
        self.model = line
        self.lineShape = None

        #self.aa = True
        self.aa = False

        self.updateItem()
        self.model.installUpdateHook(self)

    def paint(self, painter, option, widget):
        #scale = painter.deviceMatrix().m11()
        transform = painter.transform()
        scale = abs(transform.m11())+abs(transform.m12())
        #scale = abs(option.matrix.m11())+abs(option.matrix.m12())
        #print scale
        layer = self.model.layer
        pen = QtGui.QPen(layer.view.pen)
        if not self.parentItem() and self.selected:
            pen.setColor(self.model.layers.layerByName('selection', 'drawing').view.color)
        width = layer.lineWidth
        pixelWidth = layer.linePixelWidth
        if width > 0:
            pen.setWidth(max(scale*width, pixelWidth))

        painter.setPen(pen)
        brush = QtGui.QBrush(self.model.layer.view.brush)
        brush.setMatrix(painter.worldMatrix().inverted()[0])
        painter.setBrush(brush)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, self.aa)
        painter.drawLine(self.lineShape)
        if not self.parentItem() and self.preSelected:
            pen = QtGui.QPen(self.model.layers.layerByName('preselection', 'drawing').view.pen)
            if width > 0:
                pen.setWidth(max(scale*width, pixelWidth))
            painter.setPen(pen)
            painter.drawLine(self.lineShape)

    def updateItem(self):
        #self.prepareGeometryChange()
        l = self.model
        uu = float(l.diagram.uu)
        self.lineShape = QtCore.QLineF(
            l.x1/uu, l.y1/uu, l.x2/uu, l.y2/uu)
        self.setZValue(l.layer.zValue)
        #self._width = l.width
        #self.setLine(self.lineShape)
        self.updateBoundingRect()
        #self._boundingRect = QtGui.QGraphicsLineItem.boundingRect(self)
        self.update()

    def updateBoundingRect(self):
        self.prepareGeometryChange()
        l = self.lineShape
        d = 1e-20
        x = min(l.x1(), l.x2())
        w = abs(l.x1()-l.x2())+d
        y = min(l.y1(), l.y2())
        h = abs(l.y1()-l.y2())+d
        
        self._boundingRect = QtCore.QRectF(x, y, w, h)
        a = self.model.layer.lineWidth/2.0
        self._boundingRect.adjust(-a,-a,a,a)
        

class RectItem(BaseItem):
    def __init__(self, rect, parent=None):
        BaseItem.__init__(self, parent)
        self.model = rect
        self.rectShape = None

        #self.aa = True
        self.aa = False

        self.updateItem()
        self.model.installUpdateHook(self)

    def paint(self, painter, option, widget):
        #scale = painter.deviceMatrix().m11()
        transform = painter.transform()
        scale = abs(transform.m11())+abs(transform.m12())
        #scale = abs(option.matrix.m11())+abs(option.matrix.m12())
        #print scale

        layer = self.model.layer
        pen = QtGui.QPen(layer.view.pen)
        #if self.selected:
        #    pen.setColor(self.model.layers.layerByName('selection', 'drawing').view.color)
        width = layer.lineWidth
        pixelWidth = layer.linePixelWidth
        if width > 0:
            pen.setWidth(max(scale*width, pixelWidth))

        painter.setPen(pen)
        brush = QtGui.QBrush(self.model.layer.view.brush)
        brush.setMatrix(painter.worldMatrix().inverted()[0])
        painter.setBrush(brush)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, self.aa)
        painter.drawRect(self.rectShape)
        if not self.parentItem() and self.selected:
            pen = QtGui.QPen(self.model.layers.layerByName('selection', 'drawing').view.pen)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def updateItem(self):
        #self.prepareGeometryChange()
        r = self.model
        uu = float(r.diagram.uu)
        self.rectShape = QtCore.QRectF(
            r.x/uu, r.y/uu, r.w/uu, r.h/uu)
        self.setZValue(r.layer.zValue)
        #self._width = l.width()
        #self.setRect(self._boundingRectShape)
        #self.update(self.boundingRect())
        #def setLineWidth(self, width):
        #self.width = width
        #self._boundingRect = QtGui.QGraphicsRectItem.boundingRect(self)
        self.updateBoundingRect()
        self.update(self.boundingRect())

    def updateBoundingRect(self):
        self.prepareGeometryChange()
        self._boundingRect = QtCore.QRectF(self.rectShape)
        a = self.model.layer.lineWidth/2.0
        self._boundingRect.adjust(-a,-a,a,a)
        
class EllipseItem(BaseItem):
    def __init__(self, ellipse, parent=None):
        BaseItem.__init__(self, parent)
        self.model = ellipse
        #self.aa = True
        self.aa = False

        self.updateItem()
        self.model.installUpdateHook(self)

    def paint(self, painter, option, widget):
        #scale = painter.deviceMatrix().m11()
        transform = painter.transform()
        scale = abs(transform.m11())+abs(transform.m12())
        #scale = abs(option.matrix.m11())+abs(option.matrix.m12())
        #print matrix.m11()

        layer = self.model.layer
        pen = QtGui.QPen(layer.view.pen)
        width = layer.lineWidth
        pixelWidth = layer.linePixelWidth
        if width > 0:
            pen.setWidth(max(scale*width, pixelWidth))

        painter.setPen(pen)
        brush = QtGui.QBrush(self.model.layer.view.brush)
        brush.setMatrix(painter.worldMatrix().inverted()[0])
        painter.setBrush(brush)
        #painter.setRenderHint(QtGui.QPainter.Antialiasing, self.aa)
        #self.pen.setCosmetic(True)
        #painter.setPen(self.pen())
        painter.drawEllipse(self.ellipseRect)
        if not self.parentItem() and self.selected:
            pen = QtGui.QPen(self.model.layers.layerByName('selection', 'drawing').view.pen)
            painter.setPen(pen)
            brush = QtGui.QBrush(self.model.layers.layerByName('selection', 'drawing').view.brush)
            painter.setBrush(brush)
            painter.drawRect(self.boundingRect())

    def updateItem(self):
        #self.prepareGeometryChange()
        e = self.model
        self.updateBoundingRect()
        #self.setRect(e.x/uu-cx/2.0, e.y/uu-cy/2.0, cx, cy)
        self.setZValue(e.layer.zValue)
        self.update(self.boundingRect())

    def updateBoundingRect(self):
        self.prepareGeometryChange()
        e = self.model
        uu = float(e.diagram.uu)
        cx = e.radiusX/uu
        cy = e.radiusY/uu
        self._boundingRect = QtCore.QRectF(e.x/uu-cx/2.0, e.y/uu-cy/2.0, cx, cy)
        self.ellipseRect = QtCore.QRectF(self._boundingRect)
        a = self.model.layer.lineWidth/2.0
        self._boundingRect.adjust(-a,-a,a,a)
        
        
class EllipseArcItem(BaseItem):
    def __init__(self, ellipseArc, parent=None):
        BaseItem.__init__(self, parent)
        self.model = ellipseArc
        #self.aa = True
        self.aa = False

        self.updateItem()
        self.model.installUpdateHook(self)

    def paint(self, painter, option, widget):
        #scale = painter.deviceMatrix().m11()
        transform = painter.transform()
        scale = abs(transform.m11())+abs(transform.m12())
        #scale = abs(option.matrix.m11())+abs(option.matrix.m12())
        #print matrix.m11()

        layer = self.model.layer
        pen = QtGui.QPen(layer.view.pen)
        #if self.selected:
        #    pen.setColor(self.model.layers.layerByName('selection', 'drawing').view.color)
        width = layer.lineWidth
        pixelWidth = layer.linePixelWidth
        if width > 0:
            pen.setWidth(max(scale*width, pixelWidth))


        painter.setPen(pen)
        #painter.setRenderHint(QtGui.QPainter.Antialiasing, self.aa)
        ##self.pen.setCosmetic(True)
        ##painter.setPen(self.pen)
        painter.drawArc(self.ellipseRect, self.startAngle, self.spanAngle)
        painter.setPen(QtGui.QPen())
        brush = QtGui.QBrush(self.model.layer.view.brush)
        brush.setMatrix(painter.worldMatrix().inverted()[0])
        painter.setBrush(brush)
        #painter.drawRect(self.boundingRect())
        if not self.parentItem() and self.selected:
            pen = QtGui.QPen(self.model.layers.layerByName('selection', 'drawing').view.pen)
            painter.setPen(pen)
            brush = QtGui.QBrush(self.model.layers.layerByName('selection', 'drawing').view.brush)
            painter.setBrush(brush)
            painter.drawRect(self.boundingRect())

    def updateItem(self):
        #self.prepareGeometryChange()
        e = self.model
        self.startAngle = -e.startAngle*16
        self.spanAngle = -e.spanAngle*16
        self.updateBoundingRect()
        self.setZValue(e.layer.zValue)
        self.update(self.boundingRect())

    def updateBoundingRect(self): #needs tightening
        self.prepareGeometryChange()
        e = self.model
        uu = float(e.diagram.uu)
        cx = e.radiusX/uu
        cy = e.radiusY/uu
        self._boundingRect = QtCore.QRectF(
            e.x/uu-cx/2.0, e.y/uu-cy/2.0, cx, cy)
        self.ellipseRect = QtCore.QRectF(self._boundingRect)
        a = self.model.layer.lineWidth/2.0
        self._boundingRect.adjust(-a,-a,a,a)

    def shape(self):
        path = QtGui.QPainterPath()
        path.moveTo(self.lineShape.p1());
        path.lineTo(self.lineShape.p2());
        return path
        #return qt_graphicsItem_shapeFromPath(path, d->pen);
        
        
#class InstanceItem(QtGui.QGraphicsItemGroup):
#    def __init__(self, instance, parent=None):
#        QtGui.QGraphicsItemGroup.__init__(self, parent)
class InstanceItem(BaseItem):
    def __init__(self, instance, parent=None):
        BaseItem.__init__(self, parent)
        self.model = instance
        self.cellView = self.model.instanceCellView
        #print self.__class__.__name__, instance, instance.instanceLibraryPath, instance.instanceCellName, instance.instanceCellViewName, self._cellView
        self.uu = float(self.cellView.uu)
        self._boundingRect = QtCore.QRectF()
        self.selectShape = QtGui.QPainterPath()
        #self.setZValue(self.model.layer.zValue)
        self.setHandlesChildEvents(True)
        self.model.itemAdded(self)
        self.cellView.instanceItemAdded(self)

    #@property
    #def cellView(self):
    #    return self._cellView
        
    #@property
    #def selectShape(self):
    #    #self._selectShape = QtGui.QPainterPath()
    #    #self._selectShape.addRect(self._boundingRect)
    #    return self._selectShape

    def instanceRemoved(self):
        #self.model = None
        #self._cellView = None
        self.scene().removeItem(self)
        
    def paint(self, painter, option, widget):
        if not self.parentItem():
            if self.selected:
                pen = QtGui.QPen(self.model.layers.layerByName('selection', 'drawing').view.pen)
                painter.setPen(pen)
                #painter.drawRect(self.boundingRect())
                painter.drawPath(self.selectShape)
            if self.preSelected:
                pen = QtGui.QPen(self.model.layers.layerByName('preselection', 'drawing').view.pen)
                painter.setPen(pen)
                #painter.drawRect(self.boundingRect())
                painter.drawPath(self.selectShape)


    #def installTransformChangeHook(self, cb):
    #    self._transformHooks.add(cb)

    def addElem(self, e):
        #self.prepareGeometryChange()
        print 'Unknown element type', e

    def addLine(self, l):
        #self.prepareGeometryChange()
        #line = LineItem(QtCore.QLineF(l.x1/self.uu, l.y1/self.uu, l.x2/self.uu, l.y2/self.uu), None)
        line = LineItem(l, self)
        #print line.boundingRect()
        line.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent, True)
        #line.setLineWidth(0.0)
        #self.addToGroup(line)
        self.updateBoundingRect()

    def addRect(self, r):
        #self.prepareGeometryChange()
        #rect = QtGui.QGraphicsRectItem(QtCore.QRectF(r.x/self.uu, r.y/self.uu, r.w/self.uu, r.h/self.uu), None)
        rect = RectItem(r, self)
        rect.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent, True)
        #self.addToGroup(rect)
        self.updateBoundingRect()

    def addEllipse(self, e):
        #self.prepareGeometryChange()
        ellipse = EllipseItem(e, self)
        ellipse.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent, True)
        #self.addToGroup(ellipse)
        self.updateBoundingRect()

    def addEllipseArc(self, e):
        #self.prepareGeometryChange()
        ellipseArc = EllipseArcItem(e, self)
        ellipseArc.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent, True)
        #self.addToGroup(ellipseArc)
        self.updateBoundingRect()

    def addCustomPath(self, p):
        #self.prepareGeometryChange()
        path = CustomPathItem(p, self)
        path.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent, True)
        #self.addToGroup(path)
        self.updateBoundingRect()

    def addPin(self, p):
        #self.prepareGeometryChange()
        line = LineItem(p, self)
        line.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent, True)
        #self.addToGroup(line)
        self.updateBoundingRect()

    def addLabel(self, l):
        #return
        #self.prepareGeometryChange()
        label = TextItem(l, self)
        label.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent, True)
        #self.addToGroup(label)
        label.updateMatrix()
        self.updateBoundingRect()

    def addAttributeLabel(self, a):
        #return
        #self.prepareGeometryChange()
        attr = TextItem(a, self)
        attr.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent, True)
        #self.addToGroup(attr)
        attr.updateMatrix()
        self.updateBoundingRect()

    def updateItem(self):
        self.updateMatrix()
        self.update(self.boundingRect())

    def updateMatrix(self):
        #self.prepareGeometryChange()
        for c in self.childItems():
            if (isinstance(c, TextItem) or
                isinstance(c, InstanceItem)):
                c.updateMatrix()
        self.updateBoundingRect()
        
    def updateBoundingRect(self):
        #import sys
        self.prepareGeometryChange()
        self._boundingRect = QtCore.QRectF()
        shapeRect = QtCore.QRectF()
        #self._boundingRect = childrenBoundingRect()  # missing for some reason
        for c in self.childItems():
            r = c.boundingRect()
            pos = c.pos()
            matrix = c.transform() * QtGui.QTransform().translate(pos.x(), pos.y())
            self._boundingRect = self._boundingRect | matrix.mapRect(r)
            #sys.stderr.write(str(self._boundingRect) + '\n')
            #if (not isinstance(c, TextItem) and
                #not isinstance(c, InstanceItem)):
                #shapeRect = shapeRect | matrix.mapRect(r)
            shapeRect = shapeRect | matrix.mapRect(r)
            self.selectShape = QtGui.QPainterPath()
            self.selectShape.addRect(shapeRect)
        self.update()
                
