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
from Database.Primitives import *

from random import random

class LayerView():
    def __init__(self, layer):
        self.setLayer(layer)

    def setLayer(self, layer):
        self._layer = layer
        w = 16
        h = 16

        pixmap = QtGui.QPixmap(w, h)
        painter = QtGui.QPainter(pixmap)
        painter.eraseRect(0, 0, w, h)
        self._pen = QtGui.QPen()
        #self._pen.setStyle(QtCore.Qt.NoPen)
        #self._pen.setStyle(QtCore.Qt.SolidLine)
        #self._pen.setStyle(QtCore.Qt.DashLine)
        #self._pen.setStyle(QtCore.Qt.DashDotDotLine)
        #print self._pen.dashPattern()
        style = layer.linePattern().style()
        if (style == LinePattern.NoLine):
            self._pen.setStyle(QtCore.Qt.NoPen)
        elif (style == LinePattern.Solid):
            self._pen.setStyle(QtCore.Qt.SolidLine)
        elif (style == LinePattern.Dash):
            self._pen.setStyle(QtCore.Qt.DashLine)
        elif (style == LinePattern.Dot):
            self._pen.setStyle(QtCore.Qt.DotLine)
        elif (style == LinePattern.DashDot):
            self._pen.setStyle(QtCore.Qt.DashDotLine)
        elif (style == LinePattern.DashDotDot):
            self._pen.setStyle(QtCore.Qt.DashDotDotLine)
        else:
            self._pen.setDashPattern(layer.linePattern().pattern())
        self._pen.setWidth(layer.linePattern().width())
        if layer.linePattern().endStyle() == LinePattern.FlatEnd:
            self._pen.setCapStyle(QtCore.Qt.FlatCap)
            self._pen.setJoinStyle(QtCore.Qt.BevelJoin)
        elif layer.linePattern().endStyle() == LinePattern.SquareEnd:
            self._pen.setCapStyle(QtCore.Qt.SquareCap)
            self._pen.setJoinStyle(QtCore.Qt.MiterJoin)
        else:
            self._pen.setCapStyle(QtCore.Qt.RoundCap)
            self._pen.setJoinStyle(QtCore.Qt.RoundJoin)
        self._pen.setCosmetic(True)
        self._pen.setWidth(layer.linePixelWidth())

        r, g, b = layer.color().color()
        self._color = QtGui.QColor(r, g, b)
        self._pen.setColor(self._color)

        self._brush = QtGui.QBrush()
        self._brush.setColor(self._color)
        fstyle = layer.fillPattern().style()
        if (fstyle == FillPattern.NoFill):
            self._brush.setStyle(QtCore.Qt.NoBrush)
        elif (fstyle == FillPattern.Solid):
            self._brush.setStyle(QtCore.Qt.SolidPattern)
        elif (fstyle == FillPattern.Dense1):
            self._brush.setStyle(QtCore.Qt.Dense1Pattern)
        elif (fstyle == FillPattern.Dense2):
            self._brush.setStyle(QtCore.Qt.Dense2Pattern)
        elif (fstyle == FillPattern.Dense3):
            self._brush.setStyle(QtCore.Qt.Dense3Pattern)
        elif (fstyle == FillPattern.Dense4):
            self._brush.setStyle(QtCore.Qt.Dense4Pattern)
        elif (fstyle == FillPattern.Dense5):
            self._brush.setStyle(QtCore.Qt.Dense5Pattern)
        elif (fstyle == FillPattern.Dense6):
            self._brush.setStyle(QtCore.Qt.Dense6Pattern)
        elif (fstyle == FillPattern.Dense7):
            self._brush.setStyle(QtCore.Qt.Dense7Pattern)
        elif (fstyle == FillPattern.Hor):
            self._brush.setStyle(QtCore.Qt.HorPattern)
        elif (fstyle == FillPattern.Ver):
            self._brush.setStyle(QtCore.Qt.VerPattern)
        elif (fstyle == FillPattern.Cross):
            self._brush.setStyle(QtCore.Qt.CrossPattern)
        elif (fstyle == FillPattern.BDiag):
            self._brush.setStyle(QtCore.Qt.BDiagPattern)
        elif (fstyle == FillPattern.FDiag):
            self._brush.setStyle(QtCore.Qt.FDiagPattern)
        elif (fstyle == FillPattern.DiagCross):
            self._brush.setStyle(QtCore.Qt.DiagCrossPattern)
        else:
            self._brush.setStyle(QtCore.Qt.NoBrush)
            #self._brush.setDashPattern(layer.linePattern().pattern())
        #self._pen.setBrush(self._brush)
        #color.red(), color.green(), color.blue()))
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawRect(1, 1, w-3, h-3)
        painter.end()
        self._icon = QtGui.QIcon(pixmap)
        self._layer.setView(self)

    def layer(self):
        return self._layer

    def color(self):
        return self._color

    def pen(self):
        if self._layer.visible():
            #self._pen.setColor(QtGui.QColor(random()*255, random()*255, random()*255))
            return self._pen
        else:
            pen = QtGui.QPen(QtCore.QtNoPen)
            return pen

    def brush(self):
        if self._layer.visible():
            return self._brush
        else:
            brush = QtGui.QBrush(QtCore.QtNoBrush)
            return brush

    def fontBrush(self):
        if self._layer.visible() and self._pen.style() != QtCore.Qt.NoPen:
            brush = QtGui.QBrush(self.color())
            return brush
        else:
            brush = QtGui.QBrush(QtCore.QtNoBrush)
            return brush

    def icon(self):
        return self._icon

class LayersView():
    def __init__(self, layers):
        self._layers = layers
        self._layerViews = set()
        self._views = set()
        layers.installUpdateViewHook(self)

    def addLayer(self, layer):
        layerView = LayerView(layer)
        self._layerViews.add(layerView)
        for v in self._views:
            v.update()

    def removeLayer(self, layer):
        self._layerViews.remove(layer.view())
        for v in self._views:
            v.update()

    def layerViews(self):
        return self._layerViews

    def installUpdateViewsHook(self, view):
        self._views.add(view)
