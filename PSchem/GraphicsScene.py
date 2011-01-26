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

from PyQt4 import QtCore, QtGui
from PSchem.GraphicsItems import *
from Database.Primitives import *

class GraphicsScene(QtGui.QGraphicsScene):
    def __init__(self, design):
        QtGui.QGraphicsView.__init__(self)
        self._design = design
        self.uu = float(self._design.cellView().uu())

        self._design.installUpdateHook(self)

    def updateScene(self):
        pass
        
    def design(self):
        return self._design
        
    def cellView(self):
        return self.design().cellView()
        
    def addElem(self, e):
        print 'Unknown element type', e

    def addLine(self, l):
        #line = LineItem(QtCore.QLineF(l.x1/self.uu, l.y1/self.uu, l.x2/self.uu, l.y2/self.uu), None)
        line = LineItem(l)
        #line.setLineWidth(0.0)
        self.addItem(line)

    def addRect(self, r):
        #rect = QtGui.QGraphicsRectItem(QtCore.QRectF(r.x/self.uu, r.y/self.uu, r.w/self.uu, r.h/self.uu), None)
        rect = RectItem(r)
        #QtCore.QRectF(r.x()/self.uu, r.y()/self.uu, r.w()/self.uu, r.h()/self.uu), None)
        self.addItem(rect)

    def addEllipse(self, e):
        ellipse = EllipseItem(e)
        self.addItem(ellipse)

    def addEllipseArc(self, e):
        ellipseArc = EllipseArcItem(e)
        self.addItem(ellipseArc)

    def addCustomPath(self, p):
        path = CustomPathItem(p)
        self.addItem(path)

    def addPin(self, p):
        #line = LineItem(QtCore.QLineF(p.x1/self.uu, p.y1/self.uu, p.x2/self.uu, p.y2/self.uu), None)
        line = LineItem(p)
        #line.setLineWidth(0.0)
        self.addItem(line)

    def addNetSegment(self, n):
        #line = LineItem(QtCore.QLineF(n.x1/self.uu, n.y1/self.uu, n.x2/self.uu, n.y2/self.uu), None)
        line = LineItem(n)
        #line.setLineWidth(0.0)
        self.addItem(line)

    def addSolderDot(self, n):
        ellipse = EllipseItem(n)
        self.addItem(ellipse)

    def addLabel(self, l):
        ##return
        label = TextItem(l)
        #label.setFont(QtGui.QFont("Lucida", l.size/self.uu, QtGui.QFont.Normal, False))
        #label.setText(l.text())
        #label.setSize(l.textSize()/self.uu)
        #label.setPosition(l.x()/self.uu, l.y()/self.uu)
        #label.setAngle(l.angle())
        #label.setVisible(l.visible())
        self.addItem(label)

    def addAttributeLabel(self, a):
        ##return
        attr = TextItem(a)
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


    def addOccurrence(self, o):
        instance = o.instance()
        occurrenceItem = OccurrenceItem(o)
        occurrenceItem.translate(instance.x()/self.uu, instance.y()/self.uu)
        occurrenceItem.rotate(instance.angle())
        if instance.vMirror():
            occurrenceItem.scale(1, -1)
        if instance.hMirror():
            occurrenceItem.scale(-1, 1)
        self.addItem(occurrenceItem)
        occurrenceItem.updateMatrix()

    #def mouseMoveEvent(self, event):
    #    print str(event.pos().x()) + ' ' + str(event.pos().y())
    #    QtGui.QGraphicsScene.mouseMoveEvent(self, event)

