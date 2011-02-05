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

class Lasso(QtGui.QGraphicsRectItem):
    def __init__(self, widget, pos=None, parent=None):
        QtGui.QGraphicsRectItem.__init__(self, parent)

        self._widget = widget
        self._fc = None
        self._lasso = None
        layerView = self._widget.window.database.layers.layerByName('lasso', 'drawing').view
        self.setPen(layerView.pen)
        self.setBrush(layerView.brush)
        if pos:
            self.setPos(pos)

        
    def calcUpdate(self, lasso):
        x1 = lasso.left()
        x2 = lasso.right()
        y1 = lasso.top()
        y2 = lasso.bottom()
        adj = self._widget.gridSize() * 0.01
        rectList = [
            QtCore.QRectF(x1-adj, y1-adj, x2 - x1 + 2*adj, 2*adj),
            QtCore.QRectF(x1-adj, y2-adj, x2 - x1 + 2*adj, 2*adj),
            QtCore.QRectF(x1-adj, y1-adj, 2*adj, y2 - y1 + 2*adj),
            QtCore.QRectF(x2-adj, y1-adj, 2*adj, y2 - y1 + 2*adj)]
        return rectList

    def setPos(self, pos):
        self._fc = pos
        self.setRect(pos.x(), pos.y(), 0, 0)
        
    def pos(self):
        return self._fc
        
    def stretchTo(self, pos):
        grid = self._widget.gridSize()
        x1 = min(self._fc.x(), pos.x()) - grid / 2.0
        y1 = min(self._fc.y(), pos.y()) - grid / 2.0
        x2 = max(self._fc.x(), pos.x()) + grid / 2.0
        y2 = max(self._fc.y(), pos.y()) + grid / 2.0

        lasso = QtCore.QRectF(min(x1, x2), min(y1, y2), abs(x1-x2), abs(y1-y2))
        #print self._mousePressedPos.x(), self._mousePressedPos.y(), pos.x(), pos.y()
        if self._lasso:
            self.remove()
            #self._widget.updateScene(self.calcUpdate(self._lasso, lasso))
        #self._widget.updateScene(self.calcUpdate(lasso))
        self.setRect(lasso)
        #self.update(self.boundingRect())
        #self._lasso = lasso

    def remove(self):
        if self.rect():
            #self._widget.updateScene(
            #    self.calcUpdate(self._lasso))
            #self._lasso = None
            self.setRect(None)

    def draw(self, painter, rect):
        if self._lasso:
            layerView = self._widget.window.database.layers.layerByName('lasso', 'drawing').view
            painter.setPen(layerView.pen)
            #painter.setBrush(layerView.brush)
            painter.drawRect(self._lasso)

    #def rect(self):
    #    return self._lasso
