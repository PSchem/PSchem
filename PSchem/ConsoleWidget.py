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

import sys, traceback
from PyQt4 import QtCore, QtGui

try:
    from PSchem.Controller import Command
except ImportError:
    pass

import os
import time
import re

class StdinWrap():
    def __init__(self, console):
        self.console = console
        self.stream = sys.stdin

    def isatty(self):
        return True

    def readline(self):
        return self.console.readline()

    def read(self, n=1):
        return self.console.read(n)

class StdoutWrap():
    def __init__(self, console):
        self.console = console
        self.stream = sys.stdout

    def write(self, txt):
        self.console.write(txt)
        if self.stream.fileno() >= 0: # for Windows (pythonw.exe) compatibility
            self.stream.write(txt)

    def writeSync(self, txt, markPos = False):
        self.console.setSynchronous(True, markPos)
        self.console.write(txt)
        self.console.setSynchronous(False)
        if self.stream.fileno() >= 0:
            self.stream.write(txt)

    def isatty(self):
        return True

class StderrWrap():
    def __init__(self, console):
        self.console = console
        self.stream = sys.stderr

    def write(self, txt):
        self.console.writeErr(txt)
        if self.stream.fileno() >= 0:
            self.stream.write(txt)

    def isatty(self):
        return True

class History(list):    
    def __init__(self):
        list.__init__(self)
        self.pointer = 0
        self._transient = None

    def push(self, cmd):
        self._transient = None
        self.append(cmd)
        self.pointer += 1

    def previous(self):
        if self.pointer > 0:
            self.pointer -= 1
            val = self[self.pointer]
            return val
        else:
            return None

    def next(self):
        if (self.pointer < len(self) - 1):
            self.pointer += 1
            return self[self.pointer]
        elif self._transient:
            val = self._transient
            self._transient = None
            return val
        else:
            return None

    def setTransient(self, transient):
        self._transient = transient
        self.pointer = len(self)
        
    def transient(self):
        return self._transient
            
class ConsoleWidget(QtGui.QPlainTextEdit):
    pstrip = re.compile(r'^(>>> |\.\.\. |--- )?')
    pfirst = re.compile(r'^\S+.*\:$')
    pempty = re.compile(r'^\s*$')
    pindented = re.compile(r'^\s+.*$')

    def __init__(self, window=None):
        QtGui.QPlainTextEdit.__init__(self)

        self.inHistory = False
        self._inReadline = False
        self.history = History()
        #self.setReadOnly(True)
        self.window = window
        #self.window = None
        self.buffer = u''
        self._asyncCursorPos = None
        self._editCursorPos = None
        self._lastCursorPos = None
        self._synchronous = False
        
        # font
        self.defaultFormat = self.currentCharFormat()
        self.defaultFormat.setFontFamily("Courier")
        self.defaultFormat.setFontFixedPitch(True)
        self.setCurrentCharFormat(self.defaultFormat)

        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        
        sys.stdout = StdoutWrap(self)
        #sys.stderr = StderrWrap(self)
        sys.stdin = StdinWrap(self)

        self.menu = QtGui.QMenu(self)
        self.menu.addAction(self.trUtf8('Copy'), self.copy)
        self.menu.addAction(self.trUtf8('Paste'), self.paste)
        #self.menu.addSeparator()

        self._indent = False
        self._cmd = ''

        print self._pythonInfo()
        
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = '>>> '

        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = '... '

        sys.stdout.writeSync(sys.ps1, True)

    def _pythonInfo(self):
        return 'Python %s on %s\n' % (sys.version, sys.platform) + \
            'Type "help", "copyright", "credits" or "license" for more information.\n'
        
        
    def contextMenuEvent(self,ev):
        """
        Reimplemented to show our own context menu.
        
        @param ev context menu event (QContextMenuEvent)
        """
        self.menu.popup(ev.globalPos())
        ev.accept()


    def setSynchronous(self, synchronous, markPos = False):
        if markPos:
            self._asyncCursorPos = self.textCursor().position()
            #sys.stdout.stream.write(str(self._asyncCursorPos))
        self._synchronous = synchronous

    def write(self, txt):
        if self._synchronous or not self._asyncCursorPos:
            self.moveCursor(QtGui.QTextCursor.End)
            #frmt = QtGui.QTextCharFormat(self.defaultFormat)
            #frmt.setForeground(QtGui.QBrush(QtCore.Qt.blue))
            #self.textCursor().insertText(txt, frmt)
            self.textCursor().insertText(txt, self.defaultFormat)
            self._editCursorPos = self.textCursor().position()
        else:
            cursor = self.textCursor()
            cursor.setPosition(self._asyncCursorPos)
            self.setTextCursor(cursor)
            frmt = QtGui.QTextCharFormat(self.defaultFormat)
            frmt.setForeground(QtGui.QBrush(QtCore.Qt.gray))
            self.textCursor().insertText(txt, frmt)
            #self.textCursor().insertText(txt, self.defaultFormat)
            self._editCursorPos += self.textCursor().position() - self._asyncCursorPos
            self._asyncCursorPos = self.textCursor().position()
        self.moveCursor(QtGui.QTextCursor.End)
        self.ensureCursorVisible()

    def writeErr(self, txt):
        self.write(txt)

    def readline(self):
        text = ''
        self._inReadline = True
        while True:
            QtGui.qApp.processEvents()
            char = self.read(1)
            if len(char) > 0:
                #self.setSynchronous(True)
                #sys.stdout.write(char)
                #self.setSynchronous(False)
                text = text + str(char)
                if char == '\n':
                    break 
        self._inReadline = False
        return str(text)
            

    def read(self, count=1, acc=''):
        if acc == '':
            self.buffer = self.pstrip.sub('', self.buffer)
        lenBuf = len(self.buffer)
        if lenBuf >= count:
            str = acc + self.buffer[0:count]
            self.buffer = self.buffer[count:lenBuf]
            return str
        else:
            str = acc + self.buffer
            self.buffer = u''
            time.sleep(0.01)
            return str
            #self.read(count - len(str), str)

    def parse(self, cmd):
        #sys.stdout.writeSync(sys.ps1, True)
        res = None
        line = cmd.text()
        line = self.pstrip.sub('', line)
        empty = self.pempty.search(line)
        #self._indent = self.pfirst.search(line)
        if self._indent:
            if line == '\n':
                self._indent = False
                self.setSynchronous(True)
                try:
                    self.window.controller.execute(Command(self._cmd, 'exec'), False)
                except (StandardError) as err:
                    print traceback.format_exc()
                self.setSynchronous(False)
                sys.stdout.writeSync(sys.ps1, True)
                res = self._cmd
            else:
                sys.stdout.writeSync(sys.ps2)
                self._cmd = self._cmd + line
        else:
            first = self.pfirst.search(line)
            self._cmd = line
            if first:
                sys.stdout.writeSync(sys.ps2)
                self._indent = True
            else:
                if not empty:
                    self.setSynchronous(True)
                    try:
                        self.window.controller.execute(Command(self._cmd), False)
                    except (StandardError) as err:
                        print traceback.format_exc()
                        #print err
                    self.setSynchronous(False)
                    res = self._cmd
                sys.stdout.writeSync(sys.ps1, True)
        return res
           
    def keyPressEvent(self, event):
        text  = event.text()
        key   = event.key()
        modifier = event.modifiers()
        if modifier & QtCore.Qt.ShiftModifier:
            mode = QtGui.QTextCursor.KeepAnchor
        else:
            mode = QtGui.QTextCursor.MoveAnchor

        if key == QtCore.Qt.Key_Backspace:
            cursor = self.textCursor()
            if cursor.position() == cursor.anchor():
                if cursor.position() > self._editCursorPos:
                    cursor.deletePreviousChar()
            elif cursor.position() > self._editCursorPos:
                cursor.removeSelectedText()

        elif key == QtCore.Qt.Key_Delete:
            cursor = self.textCursor()
            if cursor.position() == cursor.anchor():
                cursor.deleteChar()
            else:
                cursor.removeSelectedText()
            
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            #self.parseInput('\n')
            
            self.moveCursor(QtGui.QTextCursor.EndOfLine)
            self.textCursor().insertText(event.text())
            self.buffer = self._getLine() + '\n'
            if not self._inReadline:
                cmd = Command(self.readline())
                cmdLine = self.parse(cmd)
                if cmdLine:
                    self.history.push(Command(cmdLine))
                
        #elif key == QtCore.Qt.Key_Tab:
        #    self.__insert_text(text)
        elif key == QtCore.Qt.Key_Left:
            cursor = self.textCursor()
            if modifier & QtCore.Qt.ControlModifier:
                cursor.movePosition(QtGui.QTextCursor.PreviousWord, mode)
            else:
                cursor.movePosition(QtGui.QTextCursor.PreviousCharacter, mode)
            if cursor.position() < self._editCursorPos:
                cursor.setPosition(self._editCursorPos, mode)
            self.setTextCursor(cursor)

        elif key == QtCore.Qt.Key_Right:
            cursor = self.textCursor()
            if modifier & QtCore.Qt.ControlModifier:
                cursor.movePosition(QtGui.QTextCursor.NextWord, mode)
            else:
                cursor.movePosition(QtGui.QTextCursor.NextCharacter, mode)
            #if cursor.position() > QtGui.QTextCursor.EndOfLine:
            #    cursor.setPosition(QtGui.QTextCursor.EndOfLine, mode)
            self.setTextCursor(cursor)

        elif key == QtCore.Qt.Key_Home:
            cursor = self.textCursor ()
            cursor.setPosition(self._editCursorPos, mode)
            self.setTextCursor(cursor)

        elif key == QtCore.Qt.Key_End:
            self.moveCursor(QtGui.QTextCursor.EndOfLine, mode)
            self.point = self.line.length()

        elif key == QtCore.Qt.Key_Up:
            if not self.history.transient():
                self.history.setTransient(Command(self._getLine()))
            cmd = self.history.previous()
            if cmd:
                text = cmd.text()
                text = text[0:len(text)-1]
                self._setLine(text)
                
        elif key == QtCore.Qt.Key_Down:
            cmd = self.history.next()
            if cmd:
                text = cmd.text()
                text = text[0:len(text)-1]
                self._setLine(text)

        elif text.length():
            self.textCursor().insertText(event.text())
        else:
            event.ignore()

            
    def _getLine(self):
        cursor = self.textCursor()
        oldPos = cursor.position()
        cursor.setPosition(self._editCursorPos)
        cursor.movePosition(QtGui.QTextCursor.EndOfLine, QtGui.QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        text = str(self.textCursor().selectedText())
        cursor.setPosition(oldPos)
        self.setTextCursor(cursor)
        return text
        
    def _setLine(self, text):
        cursor = self.textCursor()
        oldPos = cursor.position()
        cursor.setPosition(self._editCursorPos)
        cursor.movePosition(QtGui.QTextCursor.EndOfLine, QtGui.QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        cursor.removeSelectedText()
        cursor.insertText(text)
        

    def resizeEvent(self, e):
        QtGui.QPlainTextEdit.resizeEvent(self, e)
        cursor = self.textCursor()
        oldPos = cursor.position()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        cursor.setPosition(oldPos)
        self.setTextCursor(cursor)

        
    def mousePressEvent(self, e):
        self._lastCursorPos = self.textCursor().position()
        QtGui.QPlainTextEdit.mousePressEvent(self, e)

    def mouseReleaseEvent(self, e):
        QtGui.QPlainTextEdit.mouseReleaseEvent(self, e)
        if e.button() == QtCore.Qt.LeftButton:
            self.copy()
        if e.button() == QtCore.Qt.MidButton:
            self.paste()
        if self.textCursor().position() < self._editCursorPos: #.position():
            cursor = self.textCursor()
            if self._lastCursorPos:
                cursor.setPosition(self._lastCursorPos) #.position())
            self.setTextCursor(cursor)
        e.accept()

    def paste(self):
        lines = str(QtGui.qApp.clipboard().text())
        self.textCursor().insertText(lines)



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    console = ConsoleWidget()
    console.show()
    sys.exit(app.exec_())

        