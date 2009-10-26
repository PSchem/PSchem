# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from GraphicsItems import *
from Database.Primitives import *

class GraphicsScene(QtGui.QGraphicsScene):
    def __init__(self, cellView):
        QtGui.QGraphicsView.__init__(self)
        self.cellView = cellView
        self.uu = float(self.cellView.uu())

        self.cellView.installUpdateHook(self)

    def addElem(self, e):
        print 'Unknown element type', e

    def addLine(self, l):
        #line = LineItem(QtCore.QLineF(l.x1/self.uu, l.y1/self.uu, l.x2/self.uu, l.y2/self.uu), None)
        line = LineItem(l, None)
        #line.setLineWidth(0.0)
        self.addItem(line)

    def addRect(self, r):
        #rect = QtGui.QGraphicsRectItem(QtCore.QRectF(r.x/self.uu, r.y/self.uu, r.w/self.uu, r.h/self.uu), None)
        rect = RectItem(r, None)
        #QtCore.QRectF(r.x()/self.uu, r.y()/self.uu, r.w()/self.uu, r.h()/self.uu), None)
        self.addItem(rect)

    def addEllipse(self, e):
        ellipse = EllipseItem(e, None)
        self.addItem(ellipse)

    def addEllipseArc(self, e):
        ellipseArc = EllipseArcItem(e, None)
        self.addItem(ellipseArc)

    def addCustomPath(self, p):
        path = CustomPathItem(p, None)
        self.addItem(path)

    def addPin(self, p):
        #line = LineItem(QtCore.QLineF(p.x1/self.uu, p.y1/self.uu, p.x2/self.uu, p.y2/self.uu), None)
        line = LineItem(p, None)
        #line.setLineWidth(0.0)
        self.addItem(line)

    def addNetSegment(self, n):
        #line = LineItem(QtCore.QLineF(n.x1/self.uu, n.y1/self.uu, n.x2/self.uu, n.y2/self.uu), None)
        line = LineItem(n, None)
        #line.setLineWidth(0.0)
        self.addItem(line)

    def addLabel(self, l):
        label = TextItem(l, None)
        #label.setFont(QtGui.QFont("Lucida", l.size/self.uu, QtGui.QFont.Normal, False))
        #label.setText(l.text())
        #label.setSize(l.textSize()/self.uu)
        #label.setPosition(l.x()/self.uu, l.y()/self.uu)
        #label.setAngle(l.angle())
        #label.setVisible(l.visible())
        self.addItem(label)

    def addAttribute(self, a):
        attr = TextItem(a, None)
        #attr.setFont(QtGui.QFont("Lucida", a.size/self.uu, QtGui.QFont.Normal, False))
        #if a.visibleKey():
        #    attr.setText(str(a.key())+': '+str(a.value()))
        #else:
        #    attr.setText(str(a.value()))

        #attr.setSize(a.textSize()/self.uu)
        #attr.setPosition(a.x()/self.uu, a.y()/self.uu)
        #attr.setAngle(a.angle())
        #attr.setVisible(a.visible())
        self.addItem(attr)


    def addInstance(self, i):
        group = InstanceItem(i, None)
        group.translate(i.x()/self.uu, i.y()/self.uu)
        group.rotate(i.angle())
        if i.vMirror():
            group.scale(1, -1)
        if i.hMirror():
            group.scale(-1, 1)
        self.addItem(group)
        group.updateMatrix()


