# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from GraphicsItems import *
from Modes import *
from random import random


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
            self._widget.updateSceneRect(self._widget.scene.sceneRect())
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

        self.window = window
        self.initialized = False
        self.flipX = 1
        self.flipY = -1

        self.setFrameStyle(QtGui.QFrame.NoFrame)

        #self.setOptimizationFlags(QtGui.QGraphicsView.DontClipPainter)
        #self.setCacheMode(QtGui.QGraphicsView.CacheBackground)

        self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        self.setResizeAnchor(QtGui.QGraphicsView.NoAnchor)
        #self.setInteractive(False)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        #self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        self.scene = scene

        self.setScene(self.scene)

        self.grid = 1
        self.gridOffset= QtCore.QPointF(0, 0);

        self.updateSceneRect(self.scene.sceneRect())

        self._cursor = None
        self.modeStack = ModeStack(self)
        self.undoViewStack = UndoViewStack(self)

        self.mousePressedPos = None
        self.mousePressedButton = QtCore.Qt.NoButton
        #self.mouseLasso = None
        self.fit()


    #def paintEvent(self, event):
    #    QtGui.QGraphicsView.paintEvent(self, event)
    #    painter = QtGui.QPainter(self.viewport())
    #    #painter.scale(1, 1)
    #    painter.setPen(QtGui.QColor(random()*255, random()*255, random()*255))
    #    self.drawForeground2(painter, event.rect())
    #    #painter.drawRect(10, 10, 10, 10)

    def drawBackground(self, painter, rect):
        brush = self.window.database.layers().layerByName('background', 'drawing').view().brush()
        brush.setMatrix(painter.worldMatrix().inverted()[0])
        #painter.fillRect(rect, QtCore.Qt.black)
        painter.fillRect(rect, brush)
        self.drawGrid(painter, rect)


    def drawForeground(self, painter, rect):
        #painter.setCompositionMode(QtGui.QPainter.RasterOp_SourceXorDestination)
        #painter.setCompositionMode(QtGui.QPainter.CompositionMode_Xor)
        self.modeStack.top().drawLasso(painter, rect)
        if self._cursor:
            self._cursor.draw(painter)

    def updateSceneRect(self, rect):
        #viewport
        vr = self.viewport().rect()
        wr = self.rect()

        minverted = self.matrix().inverted()[0]
        sceneRect = minverted.mapRect(QtCore.QRectF(vr))

        #scale = min(vrw / rect.width(), vrh / rect.height())
        #sw = vrw / scale
        #sh = vrh / scale

        #sceneRect = QtCore.QRectF(
        #    scx-sw/2, scy-sh/2, sw, sh)
        #sceneRect = QtCore.QRectF(
        #    (vrx+vrw/2-dx)/s, (vry+dy-vrh/2)/s,
        #    vrw/s, vrh/s)
        self.setSceneRect(sceneRect)

    def drawGridInt(self, painter, x, y, xx, yy, g):
        offsX = self.gridOffset.x()
        offsY = self.gridOffset.y()
        i = int(x/g/2)*g*2
        j = int(y/g/2)*g*2
        if True:
            lines = []
            while i < xx: #i1 + 4 * g:
                x0  = round( i / g + offsX)*g
                lines.append(QtCore.QLineF(x0, y, x0, yy))
                i += 2.0*g
            while j < yy: # + 4 * g:
                y0 = round( j / g + offsY)*g
                lines.append(QtCore.QLineF(x, y0, xx, y0))
                j += 2.0 * g
            painter.drawLines(lines)
        else:
            points = []
            while i < xx: #i1 + 4 * g:
                x0  = round( i / g + offsX)*g
                j = int(y/g/2)*g*2
                while j < yy: # + 4 * g:
                    y0 = round( j / g + offsY)*g
                    points.append(QtCore.QPointF(x0, y0))
                    j += 2.0 * g
                i += 2.0*g
            painter.drawPoints(QtGui.QPolygonF(points))

    def drawGrid(self, painter, rect):
        x, y, w, h = rect.left(), rect.top(), rect.width(), rect.height()
        g = self.grid
        penMin = self.window.database.layers().layerByName('gridminor', 'drawing').view().pen()
        penMaj = self.window.database.layers().layerByName('gridmajor', 'drawing').view().pen()
        penAxes = self.window.database.layers().layerByName('axes', 'drawing').view().pen()
        gw = g * abs(self.matrix().m11())

        #penMin.setColor(QtGui.QColor(random()*255, random()*255, random()*255))
        grid = True
        if gw < 1:
            grid = False
        adj = 0.1
        xx = x + w + adj
        yy = y + h + adj
        x = x - adj
        y = y - adj
        #painter.setPen(Qt.lightGray)
        #painter.setPen(QtCore.Qt.gray)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)

        if grid:
            if gw > 5:
                painter.setPen(penMin)
                self.drawGridInt(painter, x, y, xx, yy, g)
            g *= 5
            painter.setPen(penMaj)
            self.drawGridInt(painter, x, y, xx, yy, g)
        #axis
        #painter.setPen(QtCore.Qt.darkGray)
        painter.setPen(penAxes)
        painter.drawLines(
            QtCore.QLineF(0, y, 0, yy),
            QtCore.QLineF(x, 0, xx, 0))


    def snapToGrid(self, point):
        x = round(
            point.x() / self.grid + self.gridOffset.x()) * self.grid
        y = round(
            point.y() / self.grid + self.gridOffset.y()) * self.grid
        return QtCore.QPointF(x, y)

    def mouseMoveEvent(self, event):
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
            self.window.statusBar().showMessage(
                    "x: "+str(self._cursor.x())+",\t y: "+str(self._cursor.y()), 1000)
            self._cursor.move(cursor)
            #self.modeStack.top().mouseMoveEvent(event, cursor)
        QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
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

    def move(self, dx, dy):
        if dx != 0 or dy != 0:
            self.undoViewStack.pushView(self.matrix())
            self._cursor = None
            m = self.matrix()
            vr = self.viewport().rect()
            rect = m.inverted()[0].mapRect(QtCore.QRectF(vr))
            m.translate(-self.flipX*dx*rect.width(), self.flipY*dy*rect.height())
            self.setMatrix(m)
            self.updateSceneRect(self.scene.sceneRect())


    def scale(self, scaleFactor):
        if scaleFactor != 1:
            self.undoViewStack.pushView(self.matrix())
            self._cursor = None
            #self._cursor.rst()
            m = self.matrix()
            vr = self.viewport().rect()
            vcx = vr.center().x()
            vcy = vr.center().y()
            newMatrix = QtGui.QMatrix(
                m.m11()*scaleFactor, 0, 0, m.m22()*scaleFactor,
                (m.dx()-vcx)*scaleFactor+vcx, (m.dy()-vcy)*scaleFactor+vcy)
            factor = abs(newMatrix.m11())

            if ((factor < 0.0001 and scaleFactor < 1) or
                (factor > 10000 and scaleFactor > 1)):
                return

            self.setMatrix(newMatrix)
            self.updateSceneRect(self.scene.sceneRect())


    def fitRect(self, rect):
        self.undoViewStack.pushView(self.matrix())
        self._cursor = None
        #self._cursor.rst()
        m = self.matrix()
        vp = self.viewport().rect()

        #rect = self.scene.sceneRect()
        w = rect.width()
        h = rect.height()
        if w == 0:
            w = 1
        if h == 0:
            h = 1
        #w *= 1.2
        #h *= 1.2
        #rect.adjust(-0.1*w, -0.1*h, 0.1*w, 0.1*h)

        #scale = min(vp.width()/rect.width(), vp.height()/rect.height())
        #sx = vp.center().x() - rect.center().x()*scale
        #sy = vp.center().y() + rect.center().y()*scale
        scale = min(vp.width()/w, vp.height()/h)
        sx = vp.center().x() - self.flipX*rect.center().x()*scale
        sy = vp.center().y() - self.flipY*rect.center().y()*scale

        m = QtGui.QMatrix(self.flipX*scale, 0, 0, self.flipY*scale, sx, sy)
        self.setMatrix(m)
        self.updateSceneRect(self.scene.sceneRect())

    def fit(self):
        rect = self.scene.sceneRect()
        w = rect.width()
        h = rect.height()
        self.fitRect(rect.adjusted(-0.1*w, -0.1*h, 0.1*w, 0.1*h))


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

    def resizeEvent(self, event):
        #temporary hack
        #when called from constructor viewport has an incorrect size
        #self.fit()
        pass

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
