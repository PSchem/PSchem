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

import sys
from PyQt4 import QtCore, QtGui
from PSchem.Controller import Command

class StdinWrap():
    def __init__(self, console):
        self.console = console
        self.stream = sys.stdin

    def isatty(self):
        return 1

    def readline(self):
        return self.console.readline()

class StdoutWrap():
    def __init__(self, console):
        self.console = console
        #self.stream = sys.stdout

    def write(self, txt):
        self.console.write(txt)
        #self.stream.write(txt)

class StderrWrap():
    def __init__(self, console):
        self.console = console
        self.stream = sys.stderr

    def write(self, txt):
        self.console.writeErr(txt)
        self.stream.write(txt)

class History():    
    def __init__(self):
        self.pointer = 0
        self.history = []
        
    def push(self, cmd):
        self.history.append(cmd)
        self.pointer = -1

    def pop(self):
        self.pointer = -1
        if (len(self.history) > 0):
            return self.history.pop()
        else:
            return ''

    def isTop(self):
        return (self.pointer == -1)

    def back(self):
        if (self.pointer > -len(self.history)):
            self.pointer -= 1
        return self.history[self.pointer]

    def forward(self):
        if (self.pointer < -1):
            self.pointer += 1
        return self.history[self.pointer]

class ConsoleWidget(QtGui.QWidget):
    def __init__(self, window):
        QtGui.QWidget.__init__(self)

        self.inHistory = False
        self.history = History()
        self.layout = QtGui.QHBoxLayout()
        #self.layout = QtGui.QSplitter()
        self.hlayout = QtGui.QHBoxLayout()
        self.console = QtGui.QTextEdit()
        self.console.setFontFamily("Courier")
        self.console.setReadOnly(True)
        #self.edit = QtGui.QLineEdit()
        self.edit = EditWidget(self)
        self.console.setSizePolicy(QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Expanding)) #MinimumExpanding))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.enter = QtGui.QPushButton("Enter")
        self.clear = QtGui.QPushButton("Clear")
        self.previous = QtGui.QPushButton("Previous")
        self.next = QtGui.QPushButton("Next")
        self.previous.setMaximumHeight(24)
        self.next.setMaximumHeight(24)
        #self.hlayout.addWidget(self.edit, 0)
        self.gridLayout.addWidget(self.enter, 1, 0)
        self.gridLayout.addWidget(self.clear, 1, 1)
        self.gridLayout.addWidget(self.previous, 0, 0)
        self.gridLayout.addWidget(self.next, 0, 1)
        #self.gridLayout.setRowStretch(0, 0)
        #self.gridLayout.setRowStretch(1, 1000)
        self.previous.setAutoRepeat(True)
        self.next.setAutoRepeat(True)
        self.vlayout = QtGui.QVBoxLayout()
        self.vlayout.addWidget(self.console, 5)
        self.vlayout.addWidget(self.edit, 0)
        self.hlayout.addLayout(self.vlayout)
        self.hlayout.addLayout(self.gridLayout)
        self.layout.addLayout(self.hlayout)
        self.setLayout(self.layout)

        #self.connect(self.edit, QtCore.SIGNAL("returnPressed()"),
        #             self.textParse)
        self.connect(self.enter, QtCore.SIGNAL("released()"),
                     self.textParse)
        self.connect(self.clear, QtCore.SIGNAL("released()"),
                     self.edit.clear)
        self.connect(self.previous, QtCore.SIGNAL("released()"),
                     self.historyPrev)
        self.connect(self.next, QtCore.SIGNAL("released()"),
                     self.historyNext)
        self.window = window

        #print self.edit.sizeHint()
        #print self.edit.sizePolicy().verticalPolicy()
        #print self.console.sizeHint()
        #print self.console.sizePolicy().verticalPolicy()
        sys.stdout = StdoutWrap(self)
        sys.stderr = StderrWrap(self)
        sys.stdin = StdinWrap(self)
        self.defaultFormat = self.console.currentCharFormat()


    def readline(self):
        return ''


    def error(self, message):
        fmt = self.console.currentCharFormat()
        self.console.setFontWeight(QtGui.QFont.Bold)
        self.console.setTextColor(QtGui.QColor(255, 0, 0))
        self.console.append(message)
        self.console.setCurrentCharFormat(fmt)


    def command(self, message):
        fmt = self.console.currentCharFormat()
        self.console.setFontWeight(QtGui.QFont.Bold)
        self.console.append(">>> " + message)
        self.console.setCurrentCharFormat(fmt)

    def textParse(self):
        #text = str(self.edit.text())
        text = str(self.edit.toPlainText())
        #print dir(text)
        #print text
        command = Command(text)
        self.window.controller.execute(command)
        self.history.push(command)
        #self.window.controller.parse(text)
        #self.history.push(text)
        self.edit.clear()


    def write(self, txt):
        #if (txt != "\n"):
        self.console.textCursor().insertText(txt, self.defaultFormat)
        #self.console.append(txt)
        self.console.ensureCursorVisible()


    def writeErr(self, txt):
        #frmt = QtGui.QTextCharFormat()
        frmt = QtGui.QTextCharFormat(self.defaultFormat)
        frmt.setForeground(QtGui.QBrush(QtCore.Qt.red))
        self.console.textCursor().insertText(txt, frmt)
        self.console.ensureCursorVisible()

    #def resizeEvent(self, ev):
        #self.edit.setMaximumHeight(ev.size().height()-100)
        #QtGui.QWidget.resizeEvent(self, ev)


    def historyPrev(self):
        if (not self.inHistory):
            command = Command(str(self.edit.toPlainText()))
            self.history.push(command)
        self.inHistory = True
        cmd = self.history.back()
        self.edit.setText(cmd.str())

    def historyNext(self):
        if (self.inHistory):
            if (self.history.isTop()):
                self.inHistory = False
                cmd = self.history.pop()
            else:
                cmd = self.history.forward()
            self.edit.setText(cmd.str())


class EditWidget(QtGui.QTextEdit):
    def __init__(self, console):
        QtGui.QTextEdit.__init__(self)
        self.console = console
        self.setSizePolicy(QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Preferred)) #Fixed))
        self.connect(self, QtCore.SIGNAL("textChanged()"),
                     self.calcSizeHint)

        self.setMaximumHeight(500)
        self._sizeHint = QtCore.QSize(
            300,1)

    def minimumSizeHint(self):
        return QtCore.QSize(
            100,28)

    def calcSizeHint(self):
        newHeight = self.document().size().height() + 5
        if newHeight != self._sizeHint.height():
            self.updateGeometry()
        self._sizeHint = QtCore.QSize(300, newHeight)
        self.console.console.ensureCursorVisible()
        #print newHeight, self.maximumHeight()

    def sizeHint(self):
        return self._sizeHint

    def keyPressEvent(self, event):
        text  = event.text()
        key   = event.key()
        modifier = event.modifiers()
        #print self.console.size().height()
        #print self.console.console.minimumSizeHint().height()
        #print self.sizeHint().height()
        #print modifier
        #print dir(modifier)

        if (key == QtCore.Qt.Key_Control and modifier & QtCore.Qt.ControlModifier):
            pass
        elif (key == QtCore.Qt.Key_Return and
              modifier & QtCore.Qt.ControlModifier):
            self.console.textParse()
        elif (key == QtCore.Qt.Key_Up and
              modifier & QtCore.Qt.ControlModifier):
            self.console.historyPrev()
        elif (key == QtCore.Qt.Key_Down and
              modifier & QtCore.Qt.ControlModifier):
            self.console.historyNext()
        else:
            QtGui.QTextEdit.keyPressEvent(self, event)
            #event.ignore()
        self.calcSizeHint()
