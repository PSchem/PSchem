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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PSchem.GraphicsItems import *
from PSchem.Modes import *
from random import random
import math

class UndoViewStack(list):
    def __init__(self, widget):
        list.__init__(self)
        self._widget = widget

    def isEmpty(self):
        return len(self) <= 0

    def pushView(self, matrix):
        self.append(matrix)

    def popView(self):
        if not self.isEmpty():
            matrix = self.pop()
            self._widget.cursor = None
            self._widget.setMatrix(matrix)
            self._widget.updateSceneRect(self._widget._scene.sceneRect())
            return matrix
        else:
            return None
                
    def top(self):
        return self[len(self)-1]

class Cursor():
    def __init__(self, widget, pos):
        self._widget = widget
        self.rst()
        self._cursor = None
        self.move(pos)

    def move(self, point):
        self._prev = self._cursor
        self._cursor = point
        rect = QtCore.QRectF(0, 0, 6, 6)
        rect = self._widget.matrix().inverted()[0].mapRect(rect)
        w = rect.width() #+2

        if self._prev:
            self._widget.updateScene([self._cursorUpdateRect])
        self._cursorUpdateRect = QtCore.QRectF(
            self._cursor
            - QtCore.QPointF(w/2, w/2),
            QtCore.QSizeF(w, w))
        self._widget.updateScene([self._cursorUpdateRect])

    def remove(self):
        self._widget.updateScene([self._cursorUpdateRect])
        self.rst()

    def rst(self):
        self._prev = None
        self._cursorUpdateRect = None

    def pos(self):
        return self._cursor

    def x(self):
        return self._cursor.x()

    def y(self):
        return self._cursor.y()

    def draw(self, painter):
        layerView = self._widget.window.database.layers().layerByName('cursor', 'drawing').view()
        painter.setPen(layerView.pen())
        painter.setBrush(layerView.brush())
        c = self._cursor
        rect = QtCore.QRectF(0, 0, 4, 4)
        rect = self._widget.matrix().inverted()[0].mapRect(rect)
        rectCursor = QtCore.QRectF(
            c.x() - rect.width()/2, c.y() - rect.height()/2,
            rect.width(), rect.height())
        painter.drawRect(rectCursor)

class DesignView(QtGui.QGraphicsView):
    def __init__(self, window, scene):
        QtGui.QGraphicsView.__init__(self)

        self._eventLoopMutex = QtCore.QMutex()
        #self._debug = True
        self._debug = False
        self.window = window
        self.initialized = False
        self.flipX = 1
        self.flipY = -1
        
        
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setMouseTracking(True)

        #self.setOptimizationFlags(QtGui.QGraphicsView.DontClipPainter)
        #self.setCacheMode(QtGui.QGraphicsView.CacheBackground)

        #self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        #self.setResizeAnchor(QtGui.QGraphicsView.NoAnchor)
        #self.setInteractive(False)
        #self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        #self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        self._scene = scene

        self.setScene(self._scene)

        self._gridSize = 1.0
        self._gridCache = []
        
        self._cursor = None
        self.modeStack = ModeStack(self)
        self.undoViewStack = UndoViewStack(self)

        self._lastMousePos = None
        self.mousePressedPos = None
        self.mousePressedButton = QtCore.Qt.NoButton
        
        #self.mouseLasso = None
        self.fit()
        self.undoViewStack = UndoViewStack(self)
        
    def scene(self):
        return self._scene

    def drawBackground(self, painter, rect):
        brush = self.window.database.layers().layerByName('background', 'drawing').view().brush()
        brush.setMatrix(painter.worldMatrix().inverted()[0])
        if self._debug:
            brush = QtGui.QBrush(brush)
            brush.setColor(QtGui.QColor(random()*63, random()*63, random()*63))
            #brush.setStyle(QtCore.Qt.DiagCrossPattern)
        painter.fillRect(rect, brush)
        self.drawGrid(painter, rect)


    def drawForeground(self, painter, rect):
        #painter.setCompositionMode(QtGui.QPainter.RasterOp_SourceXorDestination)
        #painter.setCompositionMode(QtGui.QPainter.CompositionMode_Xor)
        if self._cursor:
            self._cursor.draw(painter)

    def drawGridInt(self, painter, rect, gridSize):
        left, right, top, bottom = rect.left(), rect.right(), rect.top(), rect.bottom()
        gridSize2 = 2.0*gridSize
        x = round(left/gridSize2)*gridSize2
        y = round(top/gridSize2)*gridSize2
        cacheLen = len(self._gridCache)
        n = 0
        while x < right:
            if n < cacheLen:
                self._gridCache[n].setLine(x, top, x, bottom)
            else:
                self._gridCache.append(QtCore.QLineF(x, top, x, bottom))
            x += gridSize2
            n += 1
        while y < bottom:
            if n < cacheLen:
                self._gridCache[n].setLine(left, y, right, y)
            else:
                self._gridCache.append(QtCore.QLineF(left, y, right, y))
            y += gridSize2
            n += 1
        painter.drawLines(self._gridCache[0:n])

    def drawGrid(self, painter, rect):
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        penMin = self.window.database.layers().layerByName('gridminor', 'drawing').view().pen()
        penMaj = self.window.database.layers().layerByName('gridmajor', 'drawing').view().pen()
        penAxes = self.window.database.layers().layerByName('axes', 'drawing').view().pen()

        scale = abs(self.matrix().m11())
        adj = 2.0/scale #2 pixels margin
        rect.adjust(-adj, -adj, adj, adj)
        gridSize = self._gridSize
        gridSizeView = gridSize * scale

        if gridSizeView > 1.0: #major grid
            if gridSizeView > 5.0: #minor grid
                painter.setPen(penMin)
                self.drawGridInt(painter, rect, gridSize)
            gridSize *= 5.0
            painter.setPen(penMaj)
            self.drawGridInt(painter, rect, gridSize)
        #axes
        painter.setPen(penAxes)
        painter.drawLines(
            QtCore.QLineF(0, rect.top(), 0, rect.bottom()),
            QtCore.QLineF(rect.left(), 0, rect.right(), 0))


    def snapToGrid(self, point):
        gs = self._gridSize
        x = round(point.x() / gs) * gs
        y = round(point.y() / gs) * gs
        return QtCore.QPointF(x, y)

    def mouseMoveEvent(self, event):
        if not self._eventLoopMutex.tryLock():
            return
        point = self.mapToScene(event.pos())
        cursor = self.snapToGrid(point)
        if not self._cursor:
            self._cursor = Cursor(self, cursor)
        if cursor != self._cursor.pos():
            if event.buttons() & self.mousePressedButton:
                self.modeStack.top().mouseDragEvent(event, cursor)
            else:
                self.modeStack.top().mouseMoveEvent(event, cursor)
                
            #self.window.statusBar().showMessage("x: "+str(cursor.x())+",\t y: "+str(cursor.y()), 1000)
            self._cursor.move(cursor)
            self.window.statusBar().showMessage(
                    "x: "+str(self._cursor.x())+",\t y: "+str(self._cursor.y()), 1000)
            
        
        if event.buttons() & QtCore.Qt.MidButton:
            offset = self.mapToScene(self._lastMousePos) - point
            self.move(offset.x(), offset.y(), False)
        self._lastMousePos = event.pos() #point
        self._eventLoopMutex.unlock()

    def mousePressEvent(self, event):
        self._mousePressedPosView = event.pos()
        self._lastMousePos = event.pos() #point
        self.mousePressedPos = self.snapToGrid(self.mapToScene(event.pos()))
        self.mousePressedButton = event.button()
        self.mouseLasso = None
        self.modeStack.top().mousePressEvent(event, self.mousePressedPos)
        #print self.mousePressedPos.x(), self.mousePressedPos.y()

    def mouseReleaseEvent(self, event):
        pos = self.snapToGrid(self.mapToScene(event.pos()))
        #if pos == self.mousePressedPos:
        #    print pos.x(), pos.y()
        #else:
        #    print self.mousePressedPos.x(), self.mousePressedPos.y(), pos.x(), pos.y()
            
        self.mousePressedPos = None
        self.mousePressedButton = QtCore.Qt.NoButton
        self.modeStack.top().mouseReleaseEvent(event, pos)

    def checkSceneRect(self, newVisibleArea=None):
        """
        By default QGraphicsView uses a fixed scene size (derived from the scene bounding rect).
        This, plus some built-in logic forces the scene to center in the canvas when the scene is zoomed out.
        To override this behavior, this procedure changes the view's sceneRect property to be the union
        of the actual sceneRect and the viewport rect mapped in the scene coordinates.
        """
        if not newVisibleArea:
            newVisibleArea = self.mapToScene(self.viewport().rect()).boundingRect()
        vb = newVisibleArea.y()
        vt = vb + newVisibleArea.height()
        vl = newVisibleArea.x()
        vr = vl + newVisibleArea.width()
        sceneRect = self.scene().sceneRect()
        #print "viewport rect " + str(newVisibleArea)
        #print "scene rect1 " + str(sceneRect)
        sb = sceneRect.y()
        st = sb + sceneRect.height()
        sl = sceneRect.x()
        sr = sl + sceneRect.width()
        
        yb = min(vb, sb)
        yt = max(vt, st)
        xl = min(vl, sl)
        xr = max(vr, sr)

        #print "xs ", vl, vr, sl, sr, xl, xr
        #print "ys ", vb, vt, sb, st, yb, yt

        sceneRect2 = QtCore.QRectF(xl, yb, xr-xl, yt-yb)
        #print "scene rect2 " + str(sceneRect2)
        self.setSceneRect(sceneRect2)
    
    def checkScrollBars(self):
        """
        Check if the scrollBars were moved. The check is done by comparing last stored
        center point and the center point calculated from the view. Because the
        scrollBars have limited accuracy the comparison accepts center points
        that differ by <1% of the viewport size as equal.
        If the scrollBars movement is detected the stored center point is updated
        with a calculated value.
        """
        visibleArea = self.mapToScene(self.viewport().rect()).boundingRect()
        center = QtCore.QPointF(visibleArea.x() + visibleArea.width() / 2.0,
                                visibleArea.y() + visibleArea.height() / 2.0)
        diff = center - self.currentCenterPoint
        #print abs(diff.x()) / visibleArea.width()*100, abs(diff.y()) / visibleArea.height()*100
        if abs(diff.x()) > 0.01 * visibleArea.width() or abs(diff.y()) > 0.01 * visibleArea.height():
            self.currentCenterPoint = center
    
    def move(self, dx, dy, relative = True):
        if dx != 0 or dy != 0:
            #print self.currentCenterPoint
            self.undoViewStack.pushView(self.matrix())
            self._cursor = None
            self.checkScrollBars()
            visibleArea = self.mapToScene(self.viewport().rect()).boundingRect()
            ##center = QtCore.QPointF(visibleArea.x() + visibleArea.width() / 2.0,
            ##                        visibleArea.y() + visibleArea.height() / 2.0)

            if relative:
                offset = QtCore.QPointF(dx * visibleArea.width(), dy * visibleArea.height())
            else:
                offset = QtCore.QPointF(dx, dy)
            #sr = self.scene().sceneRect() #self.sceneRect()
            #if visibleArea.y() + dy * visibleArea.height() < sr.y():
            #    sr.setHeight(sr.height() + sr.y() - visibleArea.y() - dy * visibleArea.height())
            #    sr.setY(visibleArea.y() + dy * visibleArea.height())
            #    self.setSceneRect(sr)
            self.currentCenterPoint = self.currentCenterPoint + offset
            ##self.currentCenterPoint = center + offset
            self.checkSceneRect(visibleArea.translated(offset))
            self.centerOn(self.currentCenterPoint)
            #self.setCenter(self.getCenter() + offset)
            #self.centerOn(center + offset)

    def zoom(self, scaleFactor, point=None):
        if scaleFactor != 1:

            factor = abs(self.matrix().m11())
            if ((factor < 0.0001 and scaleFactor < 1) or
                (factor > 10000 and scaleFactor > 1)):
                return

            self.undoViewStack.pushView(self.matrix())
            self._cursor = None
            self.checkScrollBars()
            vr = self.mapToScene(self.viewport().rect()).boundingRect()
            cpView = QtCore.QPointF(vr.x() + vr.width() / 2.0, vr.y() + vr.height() / 2.0)
            #print self.viewport().rect()
            #print self.sceneRect()
            cp = self.currentCenterPoint
            if point:
                point = self.snapToGrid(point)
                offset = (cp - point) * (1/scaleFactor-1)
                cp = cp + offset
                self.currentCenterPoint = cp
            #print (cp.x() - cpView.x())/vr.width()*100, (cp.y() - cpView.y())/vr.height()*100
            newvr = QtCore.QRectF(cp.x() - vr.width()/2/scaleFactor, cp.y() - vr.height()/2/scaleFactor,
                vr.width()/scaleFactor, vr.height()/scaleFactor)
            self.checkSceneRect(newvr)
            self.scale(scaleFactor, scaleFactor)
            self.centerOn(cp)
            
    def fitRect(self, rect):
        self.undoViewStack.pushView(self.matrix())
        self._cursor = None
        m = self.matrix()
        vp = self.viewport().rect()
        w = max(1e-20, rect.width())
        h = max(1e-20, rect.height())
        scale = min(vp.width()/w, vp.height()/h)
        if (scale < 0.0001 or scale > 10000):
            return
        m2 = QtGui.QMatrix(self.flipX*scale, m.m12(), m.m21(), self.flipY*scale, m.dx(), m.dy())
        self.checkSceneRect()
        self.setMatrix(m2)
        self.currentCenterPoint = rect.center()
        self.centerOn(self.currentCenterPoint)
        
    def fit(self):
        rect = self.scene().sceneRect()
        w = rect.width()
        h = rect.height()
        #self.fitRect(rect)
        self.fitRect(rect.adjusted(-0.1*w, -0.1*h, 0.1*w, 0.1*h))
        self.setSceneRect(rect)
        self.currentCenterPoint = rect.center();
        self.centerOn(self.currentCenterPoint)

    def showEvent(self, event):
        """
        Widget size is incorrect when checked at construction time.
        It has to be recalculated once it is ready to be shown.
        It should be done only once, as the showEvent is also
        generated when the widget is reactivated (e.g. when switching
        MDI windows).
        """

        if not self.initialized:
            self.fit()
            self.undoViewStack = UndoViewStack(self)
            self.initialized = True
        QtGui.QGraphicsView.showEvent(self, event)

    def wheelEvent(self, event):
        scaleFactor = math.sqrt(2.0)
        point = self.mapToScene(event.pos())
        if (event.delta() > 0):
            self.zoom(scaleFactor, point)
        else:
            self.zoom(1/scaleFactor, point)
            
    def setupViewport(self, viewport):
        QtGui.QGraphicsView.setupViewport(self, viewport)
        self.fit()
        self.undoViewStack = UndoViewStack(self)
        
        
    def installActions(self):
        self.addAction(self.window.panLeftAct)
        self.addAction(self.window.panRightAct)
        self.addAction(self.window.panUpAct)
        self.addAction(self.window.panDownAct)
        self.addAction(self.window.zoomIn2Act)
        self.addAction(self.window.zoomOut2Act)
        self.addAction(self.window.fitAct)

        #self.fileMenu = self.window.menuBar().addMenu(self.tr("&View"))
        #self.fileMenu.addAction(self.panLeftAct)
        #self.fileMenu.addAction(self.panRightAct)
        #self.fileMenu.addAction(self.panUpAct)
        #self.fileMenu.addAction(self.panDownAct)

    def uninstallActions(self):
        self.removeAction(self.window.panLeftAct)
        self.removeAction(self.window.panRightAct)
        self.removeAction(self.window.panUpAct)
        self.removeAction(self.window.panDownAct)
        self.removeAction(self.window.zoomIn2Act)
        self.removeAction(self.window.zoomOut2Act)
        self.removeAction(self.window.fitAct)

        #self.fileMenu = self.window.menuBar().addMenu(self.tr("&View"))
        #self.fileMenu.addAction(self.panLeftAct)
        #self.fileMenu.addAction(self.panRightAct)
        #self.fileMenu.addAction(self.panUpAct)
        #self.fileMenu.addAction(self.panDownAct)

    def leaveEvent(self, event):
        if self._cursor:
            self._cursor.remove()
            self._cursor = None

