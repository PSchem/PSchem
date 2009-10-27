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
import os

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
        self.stream = sys.stdout

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

class ConsoleDoc(QtGui.QTextDocument):
    def __init__(self, parent = None):
        QtGui.QTextDocument.__init__(self)
        
    def setPlainText(self, txt):
        QtGui.QTextDocument.setPlainText(self, txt + "1")
        
    def setText(self, txt):
        QtGui.QTextDocument.setText(self, txt + "1")
        
class ConsoleWidget(QtGui.QPlainTextEdit):
    def __init__(self, window):
        QtGui.QPlainTextEdit.__init__(self)

        self.inHistory = False
        self.history = History()
        #self.setReadOnly(True)
        self.window = window
        # font
        self.defaultFormat = self.currentCharFormat()
        self.defaultFormat.setFontFamily("Courier")
        self.defaultFormat.setFontFixedPitch(True)
        #self.defaultFormat.setForeground(QtGui.QBrush(QtCore.Qt.white))
        #self.defaultFormat.setBackground(QtGui.QBrush(QtCore.Qt.black))
        self.setCurrentCharFormat(self.defaultFormat)
        #self.setBackground(QtGui.QBrush(QtCore.Qt.black))
        #self.setBackgroundVisible(True)
        p = self.palette();
        p.setColor(QtGui.QPalette.Base, QtCore.Qt.black);
        p.setColor(QtGui.QPalette.Text, QtCore.Qt.white);
        self.setPalette(p);
        
        #self.consoleDoc = ConsoleDoc()
        #self.consoleDoc = QtGui.QTextDocument()
        #self.setDocument(self.consoleDoc)

        self.eofKey = QtCore.Qt.Key_D
        self.line = QtCore.QString()
        self.point = 0
        
        #print self.edit.sizeHint()
        #print self.edit.sizePolicy().verticalPolicy()
        #print self.console.sizeHint()
        #print self.console.sizePolicy().verticalPolicy()
        sys.stdout = StdoutWrap(self)
        #sys.stderr = StderrWrap(self)
        sys.stdin = StdinWrap(self)
        #self.defaultFormat = self.currentCharFormat()


    def readline(self):
        return ''


    def error(self, message):
        fmt = self.currentCharFormat()
        self.setFontWeight(QtGui.QFont.Bold)
        self.setTextColor(QtGui.QColor(255, 0, 0))
        self.append(message)
        self.setCurrentCharFormat(fmt)


    def command(self, message):
        fmt = self.currentCharFormat()
        self.setFontWeight(QtGui.QFont.Bold)
        self.append(">>> " + message)
        self.setCurrentCharFormat(fmt)

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
        #self.edit.clear()


    def write(self, txt):
        #if (txt != "\n"):
        self.textCursor().insertText(txt, self.defaultFormat)
        #self.console.append(txt)
        self.ensureCursorVisible()


    def writeErr(self, txt):
        #frmt = QtGui.QTextCharFormat()
        frmt = QtGui.QTextCharFormat(self.defaultFormat)
        frmt.setForeground(QtGui.QBrush(QtCore.Qt.red))
        self.textCursor().insertText(txt, frmt)
        self.ensureCursorVisible()

    #def resizeEvent(self, ev):
        #self.edit.setMaximumHeight(ev.size().height()-100)
        #QtGui.QWidget.resizeEvent(self, ev)
    def readline(self):
        self.reading = 1
        self.__clear_line()
        self.moveCursor(QtGui.QTextCursor.End)
        while self.reading:
        #    #pass
        #    #QtGui.qApp.processOneEvent()
            QtGui.qApp.processEvents() #QtCore.QEventLoop.ExcludeUserInputEvents)
        #    #QtCore.QCoreApplication.processOneEvent()
        if self.line.length() == 0:
            return '\n'
        else:
            return str(self.line)

    def keyPressEvent(self, event):
        text  = event.text()
        key   = event.key()
        modifier = event.modifiers()
        #print modifier
        #print dir(modifier)

        if (key == QtCore.Qt.Key_Control and modifier & QtCore.Qt.ControlModifier):
            pass
        elif key == QtCore.Qt.Key_Backspace:
            if self.point:
                cursor = self.textCursor()
                cursor.movePosition(QtGui.QTextCursor.PreviousCharacter,
                                    QtGui.QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                self.color_line()
            
                self.point -= 1 
                self.line.remove(self.point, 1)

        elif key == QtCore.Qt.Key_Delete:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.NextCharacter,
                                QtGui.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            self.color_line()
                        
            self.line.remove(self.point, 1)
            
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.write('\n')
            self.reading = 0
#            if self.reading:
#                self.reading = 0
#            else:
            self.pointer = 0
            self.window.controller.parse(str(self.line))
            self.__clear_line()
                
        elif key == QtCore.Qt.Key_Tab:
            self.__insert_text(text)
        elif key == QtCore.Qt.Key_Left:
            if self.point : 
                self.moveCursor(QtGui.QTextCursor.Left)
                self.point -= 1 
        elif key == QtCore.Qt.Key_Right:
            if self.point < self.line.length():
                self.moveCursor(QtGui.QTextCursor.Right)
                self.point += 1 

        elif key == QtCore.Qt.Key_Home:
            cursor = self.textCursor ()
            cursor.setPosition(self.cursor_pos)
            self.setTextCursor (cursor)
            self.point = 0

        elif key == QtCore.Qt.Key_End:
            self.moveCursor(QtGui.QTextCursor.EndOfLine)
            self.point = self.line.length()

#        elif key == QtCore.Qt.Key_Up:
#            if len(self.history):
#                if self.pointer == 0:
#                    self.pointer = len(self.history)
#                self.pointer -= 1
#                self.__recall()
#                
#        elif key == QtCore.Qt.Key_Down:
#            if len(self.history):
#                self.pointer += 1
#                if self.pointer == len(self.history):
#                    self.pointer = 0
#                self.__recall()

        elif text.length():
            self.__insert_text(text)
            return

        else:
            QtGui.QPlainTextEdit.keyPressEvent(self, event)
#            event.ignore()

    def __insert_text(self, text):
        """
        Insert text at the current cursor position.
        """

        self.line.insert(self.point, text)
        self.point += text.length()

        cursor = self.textCursor()
        cursor.insertText(text)
        self.color_line()

    def color_line(self):
        pass

    def __clear_line(self):
        """
        Clear input line buffer
        """
        self.line.truncate(0)
        self.point = 0

    def mousePressEvent(self, e):
        """
        Keep the cursor after the last prompt.
        """
        if e.button() == QtCore.Qt.LeftButton:
            self.moveCursor(QtGui.QTextCursor.End)
        if e.button() == QtCore.Qt.MidButton:
            self.moveCursor(QtGui.QTextCursor.End)
        return

    def paste(self):
        sys.stderr.stream.write('paste\n')
        self.moveCursor(QtGui.QTextCursor.End)
        QtGui.QPlainTextEdit.keyPressEvent(self, event)
        

    def eventFilter(self, obj, ev):
        #sys.stderr.stream.write(str(obj)+ ' '+ str(ev) + '\n')
        if isinstance(ev, QtGui.QMouseEvent):
            if (int(ev.buttons()) & QtCore.Qt.MidButton):
                sys.stderr.stream.write(str(int(ev.buttons())) + '\n')
                self.midButtonPressed = True
                return False
            if (int(ev.buttons()) == 0 and self.midButtonPressed):
                self.midButtonPressed = False
                #self.moveCursor(QtGui.QTextCursor.End)
                #self.paste()
                return False
        #print obj
        #print ev
        return False

        
    def historyPrev(self):
        if (not self.inHistory):
            command = Command(str(self.edit.toPlainText()))
            self.history.push(command)
        self.inHistory = True
        cmd = self.history.back()
        #self.edit.setPlainText(cmd.str())

    def historyNext(self):
        if (self.inHistory):
            if (self.history.isTop()):
                self.inHistory = False
                cmd = self.history.pop()
            else:
                cmd = self.history.forward()
            #self.edit.setPlainText(cmd.str())


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
