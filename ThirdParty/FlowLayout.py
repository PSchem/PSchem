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

# This file was ported from a C++ FlowLayout Qt example.

# Original notice:
# /****************************************************************************
# **
# ** Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
# ** All rights reserved.
# ** Contact: Nokia Corporation (qt-info@nokia.com)
# **
# ** This file is part of the examples of the Qt Toolkit.
# **
# ** $QT_BEGIN_LICENSE:LGPL$
# ** Commercial Usage
# ** Licensees holding valid Qt Commercial licenses may use this file in
# ** accordance with the Qt Commercial License Agreement provided with the
# ** Software or, alternatively, in accordance with the terms contained in
# ** a written agreement between you and Nokia.
# **
# ** GNU Lesser General Public License Usage
# ** Alternatively, this file may be used under the terms of the GNU Lesser
# ** General Public License version 2.1 as published by the Free Software
# ** Foundation and appearing in the file LICENSE.LGPL included in the
# ** packaging of this file.  Please review the following information to
# ** ensure the GNU Lesser General Public License version 2.1 requirements
# ** will be met: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
# **
# ** In addition, as a special exception, Nokia gives you certain additional
# ** rights.  These rights are described in the Nokia Qt LGPL Exception
# ** version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
# **
# ** GNU General Public License Usage
# ** Alternatively, this file may be used under the terms of the GNU
# ** General Public License version 3.0 as published by the Free Software
# ** Foundation and appearing in the file LICENSE.GPL included in the
# ** packaging of this file.  Please review the following information to
# ** ensure the GNU General Public License version 3.0 requirements will be
# ** met: http://www.gnu.org/copyleft/gpl.html.
# **
# ** If you have questions regarding the use of this file, please contact
# ** Nokia at qt-info@nokia.com.
# ** $QT_END_LICENSE$
# **
# ****************************************************************************/

from PyQt4 import QtCore, QtGui
 
class FlowLayout(QtGui.QLayout):
    def __init__(self, parent=None, margin=None, spacing=None):
        QtGui.QLayout.__init__(self, parent)
        self.items = []
        if margin:
            self.setMargin(margin)
        if spacing:
            self.setSpacing(spacing)

    def addItem(self, item):
        self.items.append(item)

    def itemAt(self, index):
        if index >= 0 and index < len(self.items):
            return self.items[index]
        else:
            return None

    def count(self):
        return len(self.items)

    def expandingDirections(self):
        return QtCore.Qt.Vertical | QtCore.Qt.Horizontal

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        QtGui.QLayout.setGeometry(self, rect)
        self.doLayout(rect, False)

    def minimumSize(self):
        size = QtCore.QSize()
        for i in self.items:
            size = size.expandedTo(i.minimumSize())

        size = size + QtCore.QSize(2*self.margin(), 2*self.margin())
        return size

    def sizeHint(self):
        return self.minimumSize()

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for i in self.items:
            widget = i.widget()
            spaceX = self.spacing() + widget.style().layoutSpacing(
                QtGui.QSizePolicy.PushButton,
                QtGui.QSizePolicy.PushButton,
                QtCore.Qt.Horizontal)
            spaceY = self.spacing() + widget.style().layoutSpacing(
                QtGui.QSizePolicy.PushButton,
                QtGui.QSizePolicy.PushButton,
                QtCore.Qt.Vertical)
            nextX = x + i.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + i.sizeHint().width() + spaceX
                lineHeight = 0


            if not testOnly:
                i.setGeometry(QtCore.QRect(QtCore.QPoint(x, y),
                                           i.sizeHint()))

            # reducing width of a widget if larger that available area
            if not testOnly and rect.width() < i.sizeHint().width():
                i.setGeometry(
                    QtCore.QRect(QtCore.QPoint(x, y),
                                 QtCore.QSize(rect.width(),
                                              i.sizeHint().height())))

            x = nextX
            lineHeight = max(lineHeight, i.sizeHint().height())

        return y + lineHeight - rect.y()

