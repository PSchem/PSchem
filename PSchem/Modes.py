# -*- coding: utf-8 -*-

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

from ToolOptions import *

class Lasso():
    def __init__(self, widget, firstCorner):
        self._widget = widget
        self._fc = firstCorner
        self._lasso = None

    def calcUpdate(self, lasso):
        x1 = lasso.left()
        x2 = lasso.right()
        y1 = lasso.top()
        y2 = lasso.bottom()
        adj = self._widget.grid * 0.01
        rectList = [
            QtCore.QRectF(x1-adj, y1-adj, x2 - x1 + 2*adj, 2*adj),
            QtCore.QRectF(x1-adj, y2-adj, x2 - x1 + 2*adj, 2*adj),
            QtCore.QRectF(x1-adj, y1-adj, 2*adj, y2 - y1 + 2*adj),
            QtCore.QRectF(x2-adj, y1-adj, 2*adj, y2 - y1 + 2*adj)]
        return rectList

    def stretchTo(self, pos):
        grid = self._widget.grid
        x1 = min(self._fc.x(), pos.x()) - grid / 2.0
        y1 = min(self._fc.y(), pos.y()) - grid / 2.0
        x2 = max(self._fc.x(), pos.x()) + grid / 2.0
        y2 = max(self._fc.y(), pos.y()) + grid / 2.0

        lasso = QtCore.QRectF(min(x1, x2), min(y1, y2), abs(x1-x2), abs(y1-y2))
        #print self._mousePressedPos.x(), self._mousePressedPos.y(), pos.x(), pos.y()
        if self._lasso:
            self.remove()
            #self._widget.updateScene(self.calcUpdate(self._lasso, lasso))
        self._widget.updateScene(self.calcUpdate(lasso))
        self._lasso = lasso

    def remove(self):
        if self._lasso:
            self._widget.updateScene(
                self.calcUpdate(self._lasso))
            self._lasso = None

    def draw(self, painter, rect):
        if self._lasso:
            layerView = self._widget.window.database.layers().layerByName('lasso', 'drawing').view()
            painter.setPen(layerView.pen())
            #painter.setBrush(layerView.brush())
            painter.drawRect(self._lasso)

    def rect(self):
        return self._lasso


class Mode():
    def __init__(self, view):
        self._view = view
        self._optionPanel = None
        self._actions = set()
        self._mousePressedPos = None
        self._mousePressedButton = QtCore.Qt.NoButton
        self._lasso = None
        self.installActions()

    def view(self):
        return self._view

    def exitMode(self):
        if self._lasso:
            self._lasso.remove()
            self._lasso = None
        self.uninstallActions()

    def installActions(self):
        for a in self.actions():
            self._view.addAction(a)

    def uninstallActions(self):
        for a in self.actions():
            self._view.removeAction(a)

    def actions(self):
        return self._actions

    def mousePressEvent(self, event, pos = None):
        pass

    def mouseReleaseEvent(self, event, pos = None):
        pass

    def mouseMoveEvent(self, event, pos = None):
        pass

    def mouseDragEvent(self, event, pos = None):
        pass

    def drawLasso(self, painter, rect):
        if self._lasso:
            self._lasso.draw(painter, rect)


class ItemBuffer(list):
    def __init__(self, items):
        list.__init__(self, items)
        #print self
        self._pos = 0

    def current(self):
        if self._pos < len(self):
            return self[self._pos]
        else:
            return None

    def pos(self):
        return self._pos

    def setPos(self, pos):
        #print 'pos', pos
        if pos < 0 or len(self) == 0:
            self._pos = 0
            return
        if pos < len(self):
            self._pos = pos
        else:
            self.setPos(pos - len(self))

    def next(self):
        self.setPos(self._pos + 1)

class Selection(set):
    def __init__(self, items=[]):
        set.__init__(self, items)
        for i in items:
            i.setSelected(True)

    def add(self, item):
        set.add(self, item)
        item.setSelected(True)

    def remove(self, item):
        set.remove(self, item)
        item.setSelected(False)

    def __del__(self):
        for i in self:
            i.setSelected(False)
        #self = None

class SelectMode(Mode):
    def __init__(self, view):
        self._optionPanel = SelectToolOptions()
        Mode.__init__(self, view)
        self._selection = Selection()
        self._toBeSelected = None
        self._preSelected = None
        self._modifiers = None

    def findItems(self, pos):
        items = self._view.scene.items(pos)
        items = filter(lambda i: not(i.parentItem()), items)
        items = map(lambda i: i.model, items)
        items = set(items)
        if self.addMode():
            self._toBeSelected = ItemBuffer(items - self._selection)
        elif self.subtractMode():
            self._toBeSelected = ItemBuffer(items & self._selection)
        else:
            self._toBeSelected = ItemBuffer(items)

    def currentItem(self):
        item = None
        if self._toBeSelected:
            item = self._toBeSelected.current()
        return item

    def nextItem(self):
        if self._toBeSelected:
            self._toBeSelected.next()

    def closeLasso(self):
        lasso = self._lasso
        if lasso and lasso.rect():
            items = self._view.scene.items(lasso.rect(), QtCore.Qt.ContainsItemShape)
            for i in items:
                if not i.parentItem():
                    #print i
                    self._selection.add(i.model)
                    #i.model.setSelected(True)
            #self._view.fitRect(lasso.rect())
            lasso.remove()
            self._lasso = None

    def addMode(self):
        return self._modifiers & QtCore.Qt.ShiftModifier
            
    def subtractMode(self):
        return self._modifiers & QtCore.Qt.ControlModifier
            
    def mousePressEvent(self, event, pos = None):
        if pos and event.button() == QtCore.Qt.LeftButton:
            self._modifiers = event.modifiers()
            #print "pressed", pos
            self._mousePressedPos = pos

    def mouseReleaseEvent(self, event, pos = None):
        if pos and event.button() == QtCore.Qt.LeftButton:
            self._modifiers = event.modifiers()
            #print "released", pos
            if self._lasso and self._lasso.rect():
                items = self._view.scene.items(self._lasso.rect(), QtCore.Qt.ContainsItemShape)
                items = filter(lambda i: not(i.parentItem()), items)
                items = map(lambda i: i.model, items)
                self._selection = None # forces destruction
                self._selection = Selection(items)
                self._lasso.remove()
                self._lasso = None
                self._toBeSelected = None
            else:
                if not self._toBeSelected:
                    self.findItems(pos)
                item = self.currentItem()
                if not self.addMode() and not self.subtractMode():
                    self._selection = None
                    self._selection = Selection()
                if self._preSelected:
                    self._preSelected.setPreSelected(False)
                if item:
                    if self.subtractMode():
                        self._selection.remove(item)
                    else:
                        self._selection.add(item)
                self.nextItem()
                item = self.currentItem()
                if item:
                    self._preSelected = item
                    item.setPreSelected(True)

    def mouseMoveEvent(self, event, pos = None):
        if pos:
            self._modifiers = event.modifiers()
            #self._toBeSelected = None
            self.findItems(pos)
            item = self.currentItem()
            #print item, self._preSelected
            if item != self._preSelected:
                if self._preSelected:
                    self._preSelected.setPreSelected(False)
                if item:
                    self._preSelected = item
                    item.setPreSelected(True)

    def mouseDragEvent(self, event, pos = None):
        if pos: # and event.button() == QtCore.Qt.LeftButton:
            self._modifiers = event.modifiers()
            #print "dragged", pos

            if self._lasso:
                self._lasso.stretchTo(pos)
            else:
                #if event.button() == QtCore.Qt.LeftButton:
                self._lasso = Lasso(self._view, self._mousePressedPos)


class ZoomInMode(Mode):
    def __init__(self, view):
        Mode.__init__(self, view)
        #print "Select the area to zoom in"
        self._prevCursor = self.view().cursor()
        #self.view().setCursor(QtCore.Qt.PointingHandCursor)

    def exitMode(self):
        Mode.exitMode(self)
        self.view().setCursor(self._prevCursor)

    def mousePressEvent(self, event, pos = None):
        if pos and event.button() == QtCore.Qt.LeftButton:
            if not self._lasso:
                self._lasso = Lasso(self._view, pos)


    def mouseReleaseEvent(self, event, pos = None):
        if pos and event.button() == QtCore.Qt.LeftButton:
            lasso = self._lasso
            if lasso and lasso.rect():
                self._view.fitRect(lasso.rect())
                lasso.remove()
                self._lasso = None
                self._view.modeStack.popMode()

    def mouseDragEvent(self, event, pos = None):
        #if pos and event.button() == QtCore.Qt.LeftButton:
        if self._lasso:
            self._lasso.stretchTo(pos)



class ModeStack(list):
    def __init__(self, view):
        list.__init__(self)
        self._view = view
        self.push(SelectMode(view))

    def isEmpty(self):
        return len(self) <= 1

    def push(self, mode):
        self.append(mode)

    def pushZoomInMode(self):
        self.push(ZoomInMode(self._view))

    def popMode(self):
        if not self.isEmpty():
            mode = self.pop()
            mode.exitMode()
            return mode
        else:
            return None

    def top(self):
        #print len(self)-1
        return self[len(self)-1]
